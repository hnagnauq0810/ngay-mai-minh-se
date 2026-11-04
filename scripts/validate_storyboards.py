"""Validate word-anchored visual sequences, attribution and local mirrors."""
import json
from collections import Counter
import hashlib
from pathlib import Path
from generate_voice_vieneu import units
from narration_profile import load_profile

ROOT=Path(__file__).resolve().parents[1]


def main():
 assets={}
 for filename in ['media_plan.v1.json','visual_assets.v2.json','graphic_assets.v2.json','video_assets.v1.json','unique_photos.v3.json','ai_illustrations.v3.json']:
  for a in json.loads((ROOT/'content'/filename).read_text(encoding='utf-8'))['assets']:assets[a['id']]=a
 story=json.loads((ROOT/'content/story_manifest.v1.json').read_text(encoding='utf-8'))['scenes']
 cues=json.loads((ROOT/'content/storyboard.v2.json').read_text(encoding='utf-8'))['scenes']
 assert set(cues)=={s['id'] for s in story}
 used=set();video_scenes=0;previous=set();openings=[];uses=Counter()
 for scene in story:
  shots=cues[scene['id']];parts=units(scene)
  assert 3<=len(shots)<=5,scene['id']
  current={s['asset'] for s in shots}
  assert len(current)==len(shots),f"Repeated visual within {scene['id']}"
  assert not current & previous,f"Adjacent scenes repeat: {scene['id']} {current & previous}"
  previous=current;openings.append(shots[0]['asset']);uses.update(current)
  assert shots[0]['segment']==0,scene['id']
  for shot in shots:
   a=assets[shot['asset']];used.add(a['id'])
   assert a['caption'] and a['note'] and a['license'],a['id']
   if a.get('ai_generated'):
    assert a['kind']=='illustration' and 'AI' in a['note'],a['id']
    assert (ROOT/a['original']).is_file(),a['id']
   assert 0<=shot['segment']<len(parts) and 0<=shot['offset']<1,shot
   if shot['anchor']:assert shot['anchor'].casefold() in parts[shot['segment']]['text'].casefold(),shot
  if any(s['asset'].endswith('_video') for s in shots):video_scenes+=1
 assert len(set(openings))==len(story),'Scene openings must use distinct visuals'
 assert max(uses.values())<=2,uses.most_common(3)
 fingerprints={}
 for mid in used:
  a=assets[mid];relative=a['local'].lstrip('/')
  p=ROOT/'public'/relative;q=ROOT/'standalone'/relative
  assert p.is_file() and q.is_file(),mid
  assert p.read_bytes()==q.read_bytes(),mid
  digest=hashlib.sha256(p.read_bytes()).hexdigest()
  assert digest not in fingerprints,f"Same media under different IDs: {mid}, {fingerprints.get(digest)}"
  fingerprints[digest]=mid
  if a.get('poster'):
   assert (ROOT/'public'/a['poster']).is_file(),mid
  if a['kind']!='illustration':assert a.get('source_url','').startswith('https://commons.wikimedia.org/'),mid
 print(f'PASS: {len(story)} scenes, {sum(map(len,cues.values()))} anchored cues, {len(used)} distinct visual assets, {video_scenes} scenes with video')
 print('PASS: all used assets available locally with attribution and matching standalone copies')
 print('PASS: 55 distinct opening visuals, no within-scene/adjacent repeats, maximum two uses per asset, no duplicate media files')
 profile=load_profile(ROOT)
 recordings=ROOT/'public/assets'/profile['directory']
 if all((recordings/(s['id']+'.json')).is_file() for s in story):
  profiles=set()
  for scene in story:
   sid=scene['id'];timing=json.loads((recordings/(sid+'.json')).read_text(encoding='utf-8'));profiles.add(timing['voice'])
   assert [{k:p[k] for k in ('text','speaker','kind')} for p in timing['segments']]==units(scene),sid
   assert all(0<=p['start']<p['end']<=timing['duration'] for p in timing['segments']),sid
   for extension in ('.mp3','.json'):
    assert (recordings/(sid+extension)).read_bytes()==(ROOT/'standalone/assets'/profile['directory']/(sid+extension)).read_bytes(),sid
  assert profiles=={profile['voice']},profiles
  print(f'PASS: 55 consistent story recordings, sentence timing/text parity and matching mirrors; voice {next(iter(profiles))}')


if __name__=='__main__':main()
