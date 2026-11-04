"""Cache primary-source Commons search metadata for editorial visual selection."""
import argparse
import json
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
QUERIES=[
 '"Bình dân học vụ" filetype:bitmap',
 'intitle:"Chánh cương" filetype:bitmap',
 'intitle:"Lê Hồng Phong" filetype:bitmap',
 '"Dân Chúng" "1938" filetype:bitmap',
 'intitle:"Pác Bó" filetype:bitmap',
 '"1944" "Vietnam" "army" filetype:bitmap',
 '"Ho Chi Minh" "1946" "vote" filetype:bitmap',
 '"Dong Khe" "1950" filetype:bitmap',
 '"Vietnam" "1951" "congress" filetype:bitmap',
 '"Vietnam" "land reform" filetype:bitmap',
 'intitle:"Đồng Khởi" filetype:bitmap',
 '"Ho Chi Minh trail" filetype:bitmap',
 '"Vietnam" "1960" "Congress" filetype:bitmap',
 '"Hanoi" "1972" "bomb" filetype:bitmap',
 '"Saigon" "30 April 1975" filetype:bitmap',
 '"Vietnam" "1979" "border" filetype:bitmap',
 '"Vietnam" "ration coupons" filetype:bitmap',
 'intitle:"1985" intitle:"Vietnam" filetype:bitmap',
 '"Vietnam" "1986" "congress" filetype:bitmap',
 '"Vietnam" "rice harvest" filetype:bitmap',
 '"Vietnam" "students" "school" filetype:bitmap',
 '"Haiphong" "port" filetype:bitmap',
 '"Vietnam" "computer" "classroom" filetype:bitmap',
]


def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('query',nargs='*');args=parser.parse_args()
 dest=ROOT/'docs/visual_research.json'
 data=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else {}
 for query in args.query or QUERIES:
  if query in data:continue
  params=dict(action='query',format='json',generator='search',gsrsearch=query,gsrnamespace=6,gsrlimit=4,prop='imageinfo',iiprop='url|extmetadata|size',iiurlwidth=960)
  url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
  for attempt in range(4):
   try:
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NMMS/1.4 educational visual research'}),timeout=30) as response:result=json.load(response)
    break
   except urllib.error.HTTPError as exc:
    if exc.code!=429 or attempt==3:raise
    time.sleep(3*(attempt+1))
  pages=list(result.get('query',{}).get('pages',{}).values());data[query]=pages
  dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(query,flush=True)
  for page in pages:
   m=page.get('imageinfo',[{}])[0].get('extmetadata',{});plain=lambda key:re.sub('<[^>]+>','',m.get(key,{}).get('value',''))
   print(' ',page['title'],'|',plain('ImageDescription')[:160],'|',plain('LicenseShortName'),flush=True)
  time.sleep(1)


if __name__=='__main__':main()
