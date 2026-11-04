#!/usr/bin/env python3
"""Optional one-time Wikimedia Commons media localization for this site.

Requires an internet connection at build time. Use only with rights-reviewed assets.
Run: python scripts/download_commons_media.py --all
Then: python scripts/build_site.py
"""
import argparse, json, time, shutil, urllib.request, urllib.error, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
MANIFEST=ROOT/'content/media_plan.v1.json'
ASSETS=json.loads(MANIFEST.read_text(encoding='utf-8'))['assets']
parser=argparse.ArgumentParser()
parser.add_argument('--all',action='store_true',help='Fetch all media assets')
parser.add_argument('--limit',type=int,default=0,help='Small test batch')
parser.add_argument('--dry-run',action='store_true')
args=parser.parse_args()
items=ASSETS if args.all else ASSETS[:(args.limit or 3)]

def fetch(url, attempts=4):
    for attempt in range(attempts):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'NMMS-educational-story/1.3 (media review; local educational assets)'})
            with urllib.request.urlopen(req,timeout=35) as response:
                return response.read(12_000_001)
        except urllib.error.HTTPError as exc:
            if exc.code not in (429,500,502,503,504) or attempt==attempts-1: raise
            time.sleep(2**(attempt+1))

def resolve_image(item,width=960):
    # Special:Redirect may be rate limited. Resolve the canonical upload URL
    # through Commons' documented imageinfo API instead of guessing file paths.
    query=urllib.parse.urlencode({'action':'query','format':'json','titles':'File:'+item['filename'],'prop':'imageinfo','iiprop':'url','iiurlwidth':width})
    data=json.loads(fetch('https://commons.wikimedia.org/w/api.php?'+query))
    page=next(iter(data['query']['pages'].values()))
    info=page['imageinfo'][0]
    return info.get('thumburl',info['url']),info['url']

failed=[]
for i,item in enumerate(items,1):
    dst=ROOT/'public/assets/historical'/f"{item['id']}.jpg"
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.is_file() and dst.stat().st_size>512:
        mirror=ROOT/'standalone/assets/historical'/dst.name
        mirror.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(dst,mirror)
        print(f'[{i}/{len(items)}] Exists: {item["id"]}')
        continue
    if args.dry_run:
        print(f'[{i}/{len(items)}] {item["id"]}: {item["url"]}')
        continue
    try:
        for width in (960,500,330):
            preview,_=resolve_image(item,width)
            try:
                raw=fetch(preview,attempts=1)
                break
            except urllib.error.HTTPError:
                if width==330: raise
                # Some Commons files only expose cached thumbnails at smaller
                # standard sizes; prefer those to requesting a large original.
                time.sleep(2)
        if len(raw)>12_000_000: raise RuntimeError('Media > 12MB, skip')
        if not raw.startswith(b'\xff\xd8\xff'): raise RuntimeError('Not a JPEG, check URL or image license')
        pending=dst.with_suffix('.jpg.part');pending.write_bytes(raw);pending.replace(dst)
        standalone=ROOT/'standalone/assets/historical'/dst.name
        standalone.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(dst,standalone)
        print(f'[{i}/{len(items)}] Downloaded {item["id"]}: {len(raw)//1024} KiB')
    except (urllib.error.URLError, RuntimeError, TimeoutError) as exc:
        failed.append(item['id'])
        print(f'[{i}/{len(items)}] FAILED {item["id"]}: {exc}')
    time.sleep(0.4)
if failed: raise SystemExit('Missing media: '+', '.join(failed))
