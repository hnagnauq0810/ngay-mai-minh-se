#!/usr/bin/env python3
"""Pre-generate Vietnamese natural voice MP3s for the film (never ship API keys to browsers).

Official FPT.AI TTS v5: https://docs.fpt.ai/docs/vi/speech/api/text-to-speech/
The API is asynchronous: a successful POST returns an MP3 URL that may take time to become available.
No source files are uploaded to arbitrary sites; only TTS text is sent to the configured FPT endpoint.
Usage:
  export FPT_AI_KEY="..."                 # PowerShell: $env:FPT_AI_KEY="..."
  python scripts/generate_voice_fpt.py --voice banmai
  python scripts/generate_voice_fpt.py --voice leminh --start 0 --limit 3
  python scripts/generate_voice_fpt.py --dry-run
  python scripts/generate_voice_fpt.py --dramatized  # narrator + characters, requires ffmpeg

Files: public/assets/voice/<SCENE_ID>.mp3 and standalone/assets/voice/<SCENE_ID>.mp3
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
ENDPOINT='https://api.fpt.ai/hmi/tts/v5'
VOICES={'banmai','lannhi','leminh','myan','thuminh','giahuy','linhsan'}


def load_scenes():
    return json.loads((ROOT/'content/story_manifest.v1.json').read_text(encoding='utf-8'))['scenes']


def split_dialogue(raw):
    out=[]
    for line in (raw or '').splitlines():
        if ':' not in line:continue
        role,content=line.split(':',1)
        content=content.strip().strip('“”').strip()
        if content:out.append((role.strip().upper(),content))
    return out


def blocks(scene,narrator,dramatized):
    narration=scene['title']+'. '+scene['narration']
    result=[(narrator,narration)]
    for role,line in split_dialogue(scene.get('dialogue_fiction','')):
        if dramatized:
            v='thuminh' if role=='MẸ' else 'lannhi' if role=='CON' else narrator
            result.append((v,line))
        else:
            result[0]=(narrator,result[0][1]+' '+role.title()+' nói: '+line)
    return result


def post_tts(text,api_key,voice,speed):
    headers={'api_key':api_key,'voice':voice,'speed':str(speed),'format':'mp3','Content-Type':'text/plain; charset=utf-8'}
    if len(text)>5000:
        raise ValueError('TTS request over 5000 characters, split narration before requesting')
    request=urllib.request.Request(ENDPOINT, data=text.encode('utf-8'),headers=headers,method='POST')
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request,timeout=40) as response:
                data=json.loads(response.read().decode('utf-8'))
            if data.get('error') != 0 or not data.get('async'):
                raise RuntimeError('FPT TTS returned error: '+str(data.get('message','unknown')))
            url=str(data['async'])
            if not url.startswith('https://'):
                raise RuntimeError('Refusing non-HTTPS media URL from TTS service')
            return url
        except urllib.error.HTTPError as e:
            if e.code not in (429,500,502,503,504) or attempt==4:raise
            time.sleep(min(2**attempt*2,20))
    raise RuntimeError('TTS POST retries exhausted')


def fetch_mp3(url,dest,max_seconds=160):
    begin=time.monotonic()
    attempt=0
    while time.monotonic()-begin<max_seconds:
        attempt+=1
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'NMMS-voice-export/1.2'})
            with urllib.request.urlopen(req,timeout=30) as response:
                content=response.read()
                content_type=response.headers.get('Content-Type','').lower()
            if len(content)>1000 and ('audio' in content_type or content.startswith(b'ID3') or content[:2] in (b'\xff\xfb',b'\xff\xf3',b'\xff\xf2')):
                dest.write_bytes(content)
                return
        except (urllib.error.URLError,TimeoutError): pass
        time.sleep(min(3+attempt,11))
    raise TimeoutError('Audio still not available after '+str(max_seconds)+' seconds. Retry this scene later.')


def convert_segments_to_mp3(paths,dest):
    if len(paths)==1:
        shutil.copy2(paths[0],dest)
        return
    if shutil.which('ffmpeg') is None:
        raise RuntimeError('ffmpeg required for --dramatized; install ffmpeg or omit --dramatized')
    # Re-encode all clips into a consistent stream to avoid gap/codec discontinuities.
    cmd=['ffmpeg','-y','-hide_banner','-loglevel','error']
    for p in paths:cmd+=['-i',str(p)]
    filters=''.join(f'[{i}:a]aresample=44100,asetpts=PTS-STARTPTS[a{i}];' for i in range(len(paths)))
    filters+=''.join(f'[a{i}]' for i in range(len(paths)))+f'concat=n={len(paths)}:v=0:a=1[outa]'
    cmd+=['-filter_complex',filters,'-map','[outa]','-c:a','libmp3lame','-b:a','128k',str(dest)]
    subprocess.run(cmd,check=True)


def main():
    ap=argparse.ArgumentParser(description='Build 55 Vietnamese natural voice MP3s using official FPT.AI TTS')
    ap.add_argument('--voice',choices=sorted(VOICES),default='banmai',help='Narrator; Ban Mai female North is default')
    ap.add_argument('--speed',type=int,choices=range(-3,4),default=0)
    ap.add_argument('--dramatized',action='store_true',help='Use distinct mother/child voices (additional API calls)')
    ap.add_argument('--start',type=int,default=0,help='Zero-based first scene')
    ap.add_argument('--limit',type=int,default=0,help='0 means remaining scenes')
    ap.add_argument('--dry-run',action='store_true',help='Preview texts and API request counts; no key required')
    ap.add_argument('--overwrite',action='store_true',help='Recreate existing MP3 files')
    args=ap.parse_args()
    scenes=load_scenes()
    selected=scenes[args.start:args.start+args.limit if args.limit else None]
    if args.dry_run:
        report=[{'scene':sc['id'],'segments':[{'voice':v,'characters':len(t),'sample':t[:100]} for v,t in blocks(sc,args.voice,args.dramatized)]} for sc in selected]
        print(json.dumps({'scenes':len(report),'requests':sum(len(x['segments']) for x in report),'details':report},ensure_ascii=False,indent=2))
        return 0
    key=os.environ.get('FPT_AI_KEY','').strip()
    if not key:
        print('Missing FPT_AI_KEY. Set environment variable locally; never put your key in frontend JS.',file=sys.stderr)
        return 2
    output=ROOT/'public/assets/voice'
    standalone=ROOT/'standalone/assets/voice'
    output.mkdir(parents=True,exist_ok=True);standalone.mkdir(parents=True,exist_ok=True)
    failures=[]
    for i,sc in enumerate(selected, start=args.start):
        target=output/(sc['id']+'.mp3')
        if target.exists() and target.stat().st_size>1000 and not args.overwrite:
            print(f'[{i+1}/{len(scenes)}] cache: {sc["id"]}')
            shutil.copy2(target,standalone/target.name)
            continue
        print(f'[{i+1}/{len(scenes)}] synthesizing {sc["id"]} — {sc["title"]}',flush=True)
        try:
            with tempfile.TemporaryDirectory() as d:
                files=[]
                for j,(voice,text) in enumerate(blocks(sc,args.voice,args.dramatized)):
                    path=Path(d)/f'part-{j:02d}.mp3'
                    mp3url=post_tts(text,key,voice,args.speed)
                    fetch_mp3(mp3url,path)
                    files.append(path)
                convert_segments_to_mp3(files,target)
                shutil.copy2(target,standalone/target.name)
        except Exception as exc:
            failures.append(sc['id']);print(f'ERROR {sc["id"]}: {exc}',file=sys.stderr)
    print(f'Completed: {len(selected)-len(failures)}/{len(selected)}; total MP3 files: {len(list(output.glob("*.mp3")))}/55')
    if failures:
        print('Failed scene ids: '+', '.join(failures),file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':sys.exit(main())
