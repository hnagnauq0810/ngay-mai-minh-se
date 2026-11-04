#!/usr/bin/env python3
"""Render a single Vietnamese storytelling voice locally with VieNeu v3 Turbo.

Install into an isolated environment with scripts/requirements-story-voice.txt.
Samples are generated before replacing the narration. Sentence timings are saved
alongside MP3s so visual cuts follow spoken content rather than a slideshow clock.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import unicodedata
from narration_profile import load_profile

ROOT=Path(__file__).resolve().parents[1]


def units(scene):
    title=scene['title'].strip()
    if not title.endswith(('.','!','?','…')):title+='.'
    result=[{'text':title,'speaker':'NGƯỜI DẪN','kind':'title'}]
    for text in re.split(r'(?<=[.!?…])\s+',scene['narration'].strip()):
        if text.strip():result.append({'text':text.strip(),'speaker':'NGƯỜI DẪN','kind':'narration'})
    for line in scene.get('dialogue_fiction','').splitlines():
        if ':' not in line:continue
        who,text=line.split(':',1);text=text.strip().strip('“”').strip()
        if text:result.append({'text':text,'speaker':who.strip(),'kind':'dialogue'})
    return result


def main(args):
    import numpy as np
    import soundfile as sf
    from imageio_ffmpeg import get_ffmpeg_exe
    from vieneu import Vieneu
    from vieneu._v3_turbo_engine.onnx_runtime_lite import OnnxV3LiteEngine
    # HF Hub 2.x uses content-addressed symlinks. ONNX Runtime 1.31 resolves
    # those before checking companion tensor paths, so materialize the trusted
    # downloaded graph/data files together instead of weakening path validation.
    original_fetch=OnnxV3LiteEngine._fetch
    def materialized_fetch(repo,files,subfolder):
        source=original_fetch(repo,files,subfolder)
        target=ROOT/'.cache/models'/repo.replace('/','--')/(subfolder or 'root')
        target.mkdir(parents=True,exist_ok=True)
        for name in files:
            src=source/name;dest=target/name
            if not dest.is_file() or dest.stat().st_size!=src.stat().st_size:shutil.copy2(src,dest)
        return target
    OnnxV3LiteEngine._fetch=staticmethod(materialized_fetch)
    active=load_profile(ROOT)
    args.voice=args.voice or active['voice']
    directory=args.output_dir or (active['directory'] if args.voice==active['voice'] else 'voice-story-'+re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',args.voice).encode('ascii','ignore').decode().lower()).strip('-'))
    output=ROOT/'public/assets'/directory
    mirror=ROOT/'standalone/assets'/directory
    output.mkdir(parents=True,exist_ok=True);mirror.mkdir(parents=True,exist_ok=True)
    scenes=json.loads((ROOT/'content/story_manifest.v1.json').read_text(encoding='utf-8'))['scenes']
    if args.sample:scenes=scenes[:1]
    elif args.limit:scenes=scenes[:args.limit]
    print('Loading VieNeu v3 Turbo, voice '+args.voice,flush=True)
    tts=Vieneu(backend='onnx')
    print('Voices: '+str(tts.list_preset_voices()),flush=True)
    registry_path=output/'manifest.json'
    registry=json.loads(registry_path.read_text(encoding='utf-8')) if registry_path.exists() else {'provider':'VieNeu-TTS-v3-Turbo','scenes':{}}
    for scene in scenes:
        sid=scene['id'];parts=units(scene)
        if args.sample:
            parts=parts[:3]
            sid='sample-'+args.sample
        signature=hashlib.sha256(json.dumps([parts,args.voice,args.speed,'v3turbo-1'],ensure_ascii=False).encode()).hexdigest()
        dest=output/(sid+'.mp3');timing_path=output/(sid+'.json')
        if not args.overwrite and registry['scenes'].get(sid,{}).get('signature')==signature and dest.is_file() and timing_path.is_file():
            for p in [dest,timing_path]:shutil.copy2(p,mirror/p.name)
            print('CACHE '+sid,flush=True);continue
        start=time.monotonic();segments=[];timing=[];cursor=0.0
        for n,part in enumerate(parts):
            wav=np.asarray(tts.infer(part['text'],voice=args.voice),dtype=np.float32).reshape(-1)
            if len(wav)<4800 or not np.isfinite(wav).all() or np.sqrt(np.mean(wav**2))<.001:
                raise RuntimeError('Silent/invalid recording: '+sid)
            duration=len(wav)/48000
            timing.append(dict(part,start=round(cursor,4),end=round(cursor+duration,4)))
            segments.append(wav);cursor+=duration
            pause=.55 if part['kind']=='title' else .38 if part['kind']=='dialogue' or part['text'].endswith('?') else .24
            gap=np.zeros(round(pause*48000),dtype=np.float32);segments.append(gap);cursor+=pause
            print(f'  {sid} {n+1}/{len(parts)}: {duration:.1f}s',flush=True)
        data=np.concatenate(segments)
        pcm=dest.with_suffix('.wav.part');encoded=dest.with_suffix('.mp3.part')
        sf.write(str(pcm),data,48000,format='WAV',subtype='PCM_16')
        subprocess.run([get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-y','-i',str(pcm),'-af',f'atempo={args.speed}','-codec:a','libmp3lame','-b:a','96k','-ar','48000','-f','mp3',str(encoded)],check=True)
        encoded.replace(dest);pcm.unlink()
        for segment in timing:
            segment['start']=round(segment['start']/args.speed,4);segment['end']=round(segment['end']/args.speed,4)
        cursor/=args.speed
        timing_path.write_text(json.dumps({'scene_id':scene['id'],'voice':args.voice,'duration':round(cursor,4),'segments':timing},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        for p in [dest,timing_path]:shutil.copy2(p,mirror/p.name)
        registry['scenes'][sid]={'voice':args.voice,'speed':args.speed,'signature':signature,'bytes':dest.stat().st_size,'duration':round(cursor,4)}
        registry_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');shutil.copy2(registry_path,mirror/registry_path.name)
        print(f'OK {sid}: {cursor:.1f}s audio, {time.monotonic()-start:.1f}s render',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voice',help='Voice preset; defaults to the active published narration profile')
    parser.add_argument('--output-dir',help='Separate folder under assets; default is derived from the voice name')
    parser.add_argument('--speed',type=float,default=.97)
    parser.add_argument('--sample',help='Render only a short opening sample with this safe filename')
    parser.add_argument('--limit',type=int,default=0)
    parser.add_argument('--overwrite',action='store_true')
    args=parser.parse_args()
    if args.sample and not re.fullmatch(r'[a-z0-9-]+',args.sample):parser.error('Sample name must contain only lowercase letters, digits and hyphens')
    if args.output_dir and not re.fullmatch(r'[a-z0-9-]+',args.output_dir):parser.error('Output folder must contain only lowercase letters, digits and hyphens')
    main(args)
