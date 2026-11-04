"""Download attributed topic photographs replacing the diagram cutaways."""
import html
import io
import json
from pathlib import Path
import re
import shutil
import time
import urllib.parse
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]


def fetch(url):
 request=urllib.request.Request(url,headers={'User-Agent':'NMMS educational story (Wikimedia media attribution)'})
 with urllib.request.urlopen(request,timeout=40) as response:return response.read(25_000_001)


def main():
 from PIL import Image
 requests=json.loads((ROOT/'content/topic_photo_requests.v4.json').read_text(encoding='utf-8'))['assets']
 pages={}
 for p in (ROOT/'.cache/image-research').glob('*.json'):
  data=json.loads(p.read_text(encoding='utf-8'))
  pages.update({a['title'][5:]:a for a in data.get('query',{}).get('pages',{}).values() if a.get('imageinfo')})
 metadata_path=ROOT/'docs/topic_photo_sources.v4.json'
 if metadata_path.is_file():pages.update(json.loads(metadata_path.read_text(encoding='utf-8')))
 missing=[a['filename'] for a in requests if a['filename'] not in pages]
 if missing:
  q=urllib.parse.urlencode(dict(action='query',format='json',titles='|'.join('File:'+name for name in missing),prop='imageinfo',iiprop='url|extmetadata|size',iiurlwidth=960))
  data=json.loads(fetch('https://commons.wikimedia.org/w/api.php?'+q))
  pages.update({a['title'][5:]:a for a in data.get('query',{}).get('pages',{}).values() if a.get('imageinfo')})
 selected={a['filename']:pages[a['filename']] for a in requests if a['filename'] in pages}
 metadata_path.write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 assets=[];failures=[]
 for requested in requests:
  a=dict(requested);mid=a['id'];page=pages.get(a['filename'],{});info=page.get('imageinfo',[{}])[0];m=info.get('extmetadata',{})
  plain=lambda key:html.unescape(re.sub('<[^>]+>','',m.get(key,{}).get('value',''))).strip()
  if not info or not plain('LicenseShortName'):
   print('MISSING/NO LICENSE',mid,flush=True);failures.append(mid);continue
  dest=ROOT/'public/assets/topic-photos'/(mid+'.webp');dest.parent.mkdir(parents=True,exist_ok=True)
  downloaded=not dest.is_file()
  try:
   if not dest.is_file():
    urls=[info.get('thumburl')]
    if info.get('size',0)<10_000_000:urls.append(info['url'])
    last=None
    for url in dict.fromkeys(u for u in urls if u):
     try:
      raw=fetch(url);im=Image.open(io.BytesIO(raw)).convert('RGB');im.thumbnail((1600,1400));im.save(dest,'WEBP',quality=91);break
     except (urllib.error.HTTPError,urllib.error.URLError) as exc:last=exc;time.sleep(2)
    if not dest.is_file():raise last or RuntimeError('No downloadable image')
   mirror=ROOT/'standalone/assets/topic-photos'/dest.name;mirror.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,mirror)
   a.update(author=plain('Artist') or 'Không rõ tác giả',license=plain('LicenseShortName'),license_url=plain('LicenseUrl'),source_url=info['descriptionurl'],local='assets/topic-photos/'+dest.name)
   a.setdefault('note','Ảnh tư liệu hoặc bối cảnh được xác định trong chú thích; không phải ảnh của nhân vật đời thường hư cấu.' if a['kind']=='archive' else 'Ảnh hiện đại minh họa chủ đề; không phải ảnh trực tiếp sự kiện lịch sử đang kể.')
   assets.append(a);print('READY',mid,'|',plain('DateTime'),'|',plain('ImageDescription')[:180],flush=True)
  except Exception as exc:print('FAILED',mid,str(exc),flush=True);failures.append(mid)
  if downloaded:time.sleep(1)
 (ROOT/'content/topic_photos.v4.json').write_text(json.dumps({'assets':assets},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 if failures:raise SystemExit('Unresolved: '+', '.join(failures))


if __name__=='__main__':main()
