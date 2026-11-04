"""Cache category metadata for editorial selection of distinct story photographs."""
from pathlib import Path
import json
import time
import urllib.parse
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
CATEGORIES=[
 'Hanoi in the 1930s','1930 in Hanoi','1937 in Hanoi','1939 in Hanoi',
 'August Revolution','Vietnam in 1945','Ho Chi Minh in 1946',
 'Battle of Dien Bien Phu','First Indochina War',
 'Fall of Saigon','Rice production in Vietnam','Haiphong Port',
 'Vietnamese families','Schools in Vietnam','Hanoi in the 1980s',
 'Ho Chi Minh trail','Operation Linebacker II','Tet Offensive',
 'Rice fields in Vietnam','Harvesting in Vietnam','Farmers in Vietnam',
 'Factories in Vietnam','Students in Vietnam','Hanoi in the 1990s',
 'Vietnamese markets','Markets in Vietnam','Hanoi in 2024',
]


def fetch(url):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NMMS/1.4 educational image selection'}),timeout=30) as response:return json.load(response)
  except urllib.error.HTTPError as exc:
   if exc.code!=429 or attempt==3:raise
   time.sleep(4*(attempt+1))


def main():
 folder=ROOT/'.cache/image-research';folder.mkdir(parents=True,exist_ok=True)
 for index,category in enumerate(CATEGORIES):
  target=folder/f'category-{index:02d}.json'
  if target.exists():data=json.loads(target.read_text(encoding='utf-8'))
  else:
   query=urllib.parse.urlencode(dict(action='query',format='json',generator='categorymembers',gcmtitle='Category:'+category,gcmtype='file',gcmlimit=28,prop='imageinfo',iiprop='url|extmetadata|size',iiurlwidth=960))
   data=fetch('https://commons.wikimedia.org/w/api.php?'+query)
   target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(category,flush=True)
  for page in data.get('query',{}).get('pages',{}).values():print(' ',page['title'],flush=True)
  time.sleep(1.3)


if __name__=='__main__':main()
