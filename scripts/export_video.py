#!/usr/bin/env python3
"""Optional offline MP4 export, using the generated Vietnamese narration tracks.

Requires: ffmpeg, ffprobe, Pillow. Does NOT generate narration or impersonate anyone.
Example:
  python scripts/export_video.py --output video/ngay-mai-minh-se.mp4 --size 1280x720
The export uses local Wikimedia Commons images when downloaded; never exports
a generic illustration as though it were historical evidence.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import argparse, json, shutil, subprocess, tempfile, textwrap, os
ROOT=Path(__file__).resolve().parents[1]
MEDIA=json.loads((ROOT/'content/media_plan.v1.json').read_text(encoding='utf-8'))
MEDIA_BY_ID={m['id']:m for m in MEDIA['assets']}
COLORS={'HỒI I':('#1b201f','#efd0a4'),'HỒI II':('#102936','#afd3e0'),'HỒI III':('#1a3430','#bce0c2'),'PROLOGUE':('#18252d','#edcda2'),'EPILOGUE':('#18252d','#edcda2')}

def require(binary):
    if not shutil.which(binary): raise RuntimeError(f'{binary} not installed')

def fontpath():
    paths=['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf','C:/Windows/Fonts/arial.ttf']
    return next((p for p in paths if os.path.exists(p)),None)

def wrap_lines(draw,text,font,width):
    words=text.split();out=[];cur=''
    for word in words:
        candidate=(cur+' '+word).strip()
        if draw.textbbox((0,0),candidate,font=font)[2] > width and cur:
            out.append(cur);cur=word
        else:cur=candidate
    if cur:out.append(cur)
    return out

def render_card(scene,index,size,target,allow_plain=False):
    w,h=size
    bg,fg=COLORS.get(scene['act'],COLORS['PROLOGUE'])
    media_id=MEDIA['scene_media'].get(scene['id'])
    media=MEDIA_BY_ID.get(media_id) if media_id else None
    image_path=ROOT/'public/assets/historical'/f'{media_id}.jpg' if media_id else None
    if image_path and image_path.is_file():
        with Image.open(image_path) as source:
            img=ImageOps.fit(source.convert('RGB'),(w,h),method=Image.Resampling.LANCZOS,centering=(.5,.45))
        img=ImageEnhance.Contrast(img).enhance(.84)
        dark=Image.new('RGB',(w,h),'#080e14')
        img=Image.blend(img,dark,.47)
    elif allow_plain:
        img=Image.new('RGB',(w,h),bg)
    else:
        raise RuntimeError(f'Missing image {media_id} for scene {scene["id"]}. Run scripts/download_commons_media.py --all and scripts/build_site.py first.')
    d=ImageDraw.Draw(img)
    fp=fontpath()
    def make_font(s):return ImageFont.truetype(fp,s) if fp else ImageFont.load_default()
    title_font=make_font(int(h*.061));body_font=make_font(int(h*.029));small_font=make_font(int(h*.018))
    p=int(w*.09)
    d.rectangle((0,0,w,int(h*.012)),fill=fg)
    d.text((p,int(h*.13)),f'NGÀY MAI, MÌNH SẼ... · {index:02d}/55',font=small_font,fill=fg)
    d.text((p,int(h*.21)),scene['period_label'],font=small_font,fill=fg)
    title_lines=wrap_lines(d,scene['title'],title_font,w-2*p)
    y=int(h*.275)
    for line in title_lines[:3]:d.text((p,y),line,font=title_font,fill='#f5f0e6');y+=int(h*.085)
    excerpt=scene['narration'][:440].rsplit(' ',1)[0]+'…'
    lines=wrap_lines(d,excerpt,body_font,w-2*p)
    y=max(y+int(h*.047),int(h*.53))
    for line in lines[:6]:
        d.text((p,y),line,font=body_font,fill='#e1e2db');y+=int(h*.048)
    if media:
        credit=f'{media["caption"]} | {media["author"]} | {media["license"]}'
        credit_lines=wrap_lines(d,credit,small_font,w-2*p)
        for j,line in enumerate(credit_lines[:2]):
            d.text((p,int(h*.865)+j*int(h*.024)),line,font=small_font,fill='#e5dfd3')
    d.text((p,int(h*.947)),'BẢN THẢO · CẦN THẨM ĐỊNH LỊCH SỬ VÀ GIẤY PHÉP TƯ LIỆU',font=small_font,fill=fg)
    img.save(target)

def run(cmd):subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='video/ngay-mai-minh-se.mp4')
    parser.add_argument('--size',default='1280x720')
    parser.add_argument('--limit',type=int,default=0)
    parser.add_argument('--allow-plain',action='store_true',help='Allow plain title cards if archival media are not downloaded (QA only)')
    args=parser.parse_args()
    require('ffmpeg');require('ffprobe')
    size=tuple(map(int,args.size.lower().split('x')))
    if len(size)!=2 or min(size)<300:raise ValueError('Invalid --size. Example: 1280x720')
    scenes=json.loads((ROOT/'content/story_manifest.v1.json').read_text(encoding='utf-8'))['scenes']
    if args.limit: scenes=scenes[:args.limit]
    missing=[s['id'] for s in scenes if not (ROOT/'public/assets/voice'/f'{s["id"]}.mp3').exists()]
    if missing: raise RuntimeError('MP3 missing for '+', '.join(missing[:10])+'. Generate audio first.')
    dst=ROOT/args.output;dst.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        clips=[]
        for n,scene in enumerate(scenes,1):
            poster=Path(tmp)/f'{n:03d}.png';render_card(scene,n,size,poster,allow_plain=args.allow_plain)
            audio=ROOT/'public/assets/voice'/f'{scene["id"]}.mp3'
            clip=Path(tmp)/f'{n:03d}.mp4';clips.append(clip)
            # Audio determines duration, each clip shares identical video codec settings.
            run(['ffmpeg','-y','-hide_banner','-loglevel','error','-loop','1','-framerate','25','-i',str(poster),'-i',str(audio),'-c:v','libx264','-preset','veryfast','-crf','26','-r','25','-c:a','aac','-b:a','128k','-pix_fmt','yuv420p','-shortest','-movflags','+faststart',str(clip)])
            print(f'Encoded {n}/{len(scenes)}: {scene["id"]}',flush=True)
        listfile=Path(tmp)/'playlist.txt'
        listfile.write_text(''.join("file '"+str(p).replace("'", "'\\''")+"'\n" for p in clips),encoding='utf-8')
        run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(listfile),'-c','copy','-movflags','+faststart',str(dst)])
    print('Created:',dst)

if __name__=='__main__':main()
