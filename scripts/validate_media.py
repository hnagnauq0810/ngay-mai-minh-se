#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
plan=json.loads((ROOT/'content/media_plan.v1.json').read_text(encoding='utf-8'))
scenes=json.loads((ROOT/'content/story_manifest.v1.json').read_text(encoding='utf-8'))['scenes']
ids={a['id'] for a in plan['assets']}
assert len(ids)==len(plan['assets'])
assert len(scenes)==55
assert set(s['id'] for s in scenes)==set(plan['scene_media'])
assert all(mid in ids for mid in plan['scene_media'].values())
assets=[a['id'] for a in plan['assets']]
missing=[mid for mid in assets if not (ROOT/'public/assets/historical'/f'{mid}.jpg').is_file()]
assert set(plan.get('scene_review',{}))==set(s['id'] for s in scenes)
assert all(r.get('status') in ('direct','context','needs_replacement') and r.get('note') for r in plan['scene_review'].values())
print(f'PASS: {len(ids)} media references, {len(scenes)} mapped and editorially reviewed scenes.')
if missing: print(f'INFO: {len(missing)} photos not cached locally. Website will use remote Commons URLs; run scripts/download_commons_media.py --all online.')
else: print('PASS: all photos downloaded locally.')
print('NOTICE: structural validity does not prove rights clearance or historical sign-off.')
