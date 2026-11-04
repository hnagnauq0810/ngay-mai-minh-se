#!/usr/bin/env python3
"""Safe seed check and strict release gate. No packages required.
Usage:
  python3 scripts/validate_content.py            # structural check, passes demo
  python3 scripts/validate_content.py --release  # blocks release until reviewed
"""
from pathlib import Path
import json,sys,re
root=Path(__file__).resolve().parent.parent
scenes=json.loads((root/'content/story_manifest.v1.json').read_text(encoding='utf-8'))['scenes']
chapters=json.loads((root/'content/chapters.v1.json').read_text(encoding='utf-8'))['chapters']
errors=[]
ids=[s.get('id') for s in scenes];chapter_ids=[x.get('id') for x in chapters]
if len(scenes)!=55:errors.append(f'Expected 55 scenes, received {len(scenes)}')
if len(chapters)!=12:errors.append(f'Expected 12 chapters, received {len(chapters)}')
if len(set(ids))!=len(ids):errors.append('Duplicate scene IDs')
if len(set(chapter_ids))!=len(chapter_ids):errors.append('Duplicate chapter IDs')
for s in scenes:
 sid=s.get('id')
 if not re.fullmatch(r'(C\d{2}_S\d{2}|PRO_S0[12]|EPI_S0[12])',sid or ''):errors.append(f'Invalid ID: {sid}')
 for field in ['title','narration','dialogue_fiction','historical_notes','visual_direction']:
  if not str(s.get(field,'')).strip():errors.append(f'{sid}: missing {field}')
 if s.get('chapter_id') is not None and s['chapter_id'] not in chapter_ids:errors.append(f'{sid}: unknown chapter')
for chapter in chapters:
 actual=[s['id'] for s in scenes if s['chapter_id']==chapter['id']]
 if actual!=chapter['sceneIds']:errors.append(f'{chapter["id"]}: sceneIds/order mismatch')
 if not chapter.get('slug'):errors.append(f'{chapter["id"]}: missing slug')
if '--release' in sys.argv:
 for s in scenes:
  sid=s['id']
  if s['status']!='published':errors.append(f'{sid}: not published')
  if not s.get('historical_claim_ids'):errors.append(f'{sid}: missing per-claim source mapping')
 for doc in ['historical_claims.json','source_registry.json','media_registry.json','release_metadata.json']:
  if not (root/'content'/doc).exists():errors.append(f'Missing release registry: {doc}')
 if not (root/'content'/'HISTORIAN_SIGNOFF.txt').exists():errors.append('Missing historian sign-off')
if errors:
 print('CONTENT VALIDATION FAILED:')
 for err in errors[:35]:print(' -',err)
 if len(errors)>35:print(f' ... and {len(errors)-35} more')
 sys.exit(1)
print(f'PASS: {len(chapters)} chapters, {len(scenes)} unique scenes, stable IDs and content present.')
if '--release' not in sys.argv:print('NOTE: structural check only; historical review and media rights are NOT approved.')
