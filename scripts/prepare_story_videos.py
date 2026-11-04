"""Download attributed Commons footage; create silent MP4 excerpts and preview frames."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]


def main():
 from imageio_ffmpeg import get_ffmpeg_exe
 ffmpeg=get_ffmpeg_exe()
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--clips-only',action='store_true');parser.add_argument('--only',nargs='*');args=parser.parse_args()
 metadata=json.loads((ROOT/'docs/video_source_metadata.json').read_text(encoding='utf-8'))
 pages={p['title'][5:]:p for p in metadata['query']['pages'].values()}
 plan_path=ROOT/'content/video_assets.v1.json';plan=json.loads(plan_path.read_text(encoding='utf-8'))
 for asset in plan['assets']:
  if args.only and asset['id'] not in args.only:continue
  info=pages[asset['filename']]['videoinfo'][0];m=info.get('extmetadata',{});plain=lambda key:re.sub('<[^>]+>','',m.get(key,{}).get('value','')).strip()
  asset.update(source_url=info['descriptionurl'],license=plain('LicenseShortName'),author=plain('Artist').replace('Unknown authorUnknown author','Không rõ tác giả'))
  derivatives=info.get('derivatives',[])
  source=next((d for d in derivatives if d.get('transcodekey')=='480p.vp9.webm'),None) or next((d for d in derivatives if d.get('transcodekey')=='240p.vp9.webm'),None) or (derivatives[0] if derivatives else {'src':info['url']})
  url=source['src'];ext='.mov' if '.mov' in url else '.webm';cached=ROOT/'.cache/video-source'/(asset.get('source_cache',asset['id'])+ext);cached.parent.mkdir(parents=True,exist_ok=True)
  if not cached.exists():
   for attempt in range(4):
    try:
     req=urllib.request.Request(url,headers={'User-Agent':'NMMS/1.4 educational documentary excerpts'})
     with urllib.request.urlopen(req,timeout=45) as response:
      pending=cached.with_suffix(ext+'.part');total=0
      with pending.open('wb') as dest:
       while chunk:=response.read(1024*1024):
        total+=len(chunk)
        if total>100_000_000:raise RuntimeError('Preview download exceeds 100 MB')
        dest.write(chunk)
     pending.replace(cached);print('DOWNLOADED',asset['id'],total,flush=True);break
    except urllib.error.HTTPError as exc:
     if exc.code!=429 or attempt==3:raise
     time.sleep(3*(attempt+1))
  output=ROOT/'public/assets/video'/(asset['id']+'.mp4');output.parent.mkdir(parents=True,exist_ok=True)
  subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-ss',str(asset['start']),'-i',str(cached),'-t',str(asset['duration']),'-an','-vf','scale=854:480:force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2','-c:v','libx264','-preset','fast','-crf','26','-movflags','+faststart',str(output)],check=True)
  assert output.stat().st_size>5000
  mirror=ROOT/'standalone/assets/video'/output.name;mirror.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(output,mirror)
  poster=output.with_suffix('.jpg')
  subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-ss','1','-i',str(output),'-frames:v','1','-pix_fmt','yuvj420p',str(poster)],check=True);shutil.copy2(poster,mirror.with_suffix('.jpg'))
  asset.update(local='assets/video/'+output.name,poster='assets/video/'+poster.name)
  if not args.clips_only:
   frame_dir=ROOT/'tests/video_frames';frame_dir.mkdir(parents=True,exist_ok=True)
   for second in [0,10,25,45,70]:
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-ss',str(second),'-i',str(cached),'-frames:v','1','-vf','scale=320:-1',str(frame_dir/(asset['id']+'-'+str(second)+'.png'))],check=True)
  print('READY',asset['id'],output.stat().st_size,flush=True)
  plan_path.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
