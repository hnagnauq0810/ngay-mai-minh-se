#!/usr/bin/env python3
"""Generate Vietnamese MP3s with Edge TTS, without an API key.

Only story text is sent to Microsoft's online voice service. Playback uses local
files and works without a voice installed on the listener's device.
Install: python -m pip install -r scripts/requirements-audio.txt
Usage: python scripts/generate_voice_edge.py [--limit 1] [--dry-run]
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import shutil

from generate_voice_fpt import blocks, load_scenes

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'public/assets/voice'
MIRROR = ROOT / 'standalone/assets/voice'


def fingerprint(text, voice, rate):
    return hashlib.sha256(json.dumps([text, voice, rate], ensure_ascii=False).encode('utf-8')).hexdigest()


async def generate(args):
    scenes = load_scenes()[args.start:args.start + args.limit if args.limit else None]
    plan = [(s, blocks(s, args.voice, False)[0][1]) for s in scenes]
    print(f'{len(plan)} scenes, {sum(len(text) for _, text in plan)} characters, {args.voice}, rate {args.rate}', flush=True)
    if args.dry_run:
        return
    try:
        import edge_tts
    except ImportError as exc:
        raise SystemExit('Install first: python -m pip install -r scripts/requirements-audio.txt') from exc
    OUTPUT.mkdir(parents=True, exist_ok=True)
    MIRROR.mkdir(parents=True, exist_ok=True)
    registry_path = OUTPUT / 'manifest.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8')) if registry_path.exists() else {'provider': 'edge-tts', 'scenes': {}}
    semaphore = asyncio.Semaphore(args.jobs)
    failures = []

    async def render(scene, text):
        scene_id = scene['id']
        target = OUTPUT / f'{scene_id}.mp3'
        digest = fingerprint(text, args.voice, args.rate)
        old = registry['scenes'].get(scene_id, {})
        if not args.overwrite and old.get('sha256') == digest and target.exists() and target.stat().st_size == old.get('bytes', 0) > 1024:
            shutil.copy2(target, MIRROR / target.name)
            print(f'CACHE {scene_id}', flush=True)
            return
        async with semaphore:
            temp = target.with_suffix('.mp3.part')
            for attempt in range(3):
                try:
                    await asyncio.wait_for(edge_tts.Communicate(text, args.voice, rate=args.rate).save(str(temp)), timeout=90)
                    if temp.stat().st_size < 1024:
                        raise RuntimeError('Empty or incomplete MP3')
                    temp.replace(target)
                    shutil.copy2(target, MIRROR / target.name)
                    registry['scenes'][scene_id] = {'voice': args.voice, 'rate': args.rate, 'sha256': digest, 'bytes': target.stat().st_size, 'characters': len(text)}
                    # No await between snapshot and replacement: concurrent tasks
                    # cannot overwrite a newer registry with an older snapshot.
                    pending = registry_path.with_suffix('.json.tmp')
                    pending.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                    pending.replace(registry_path)
                    shutil.copy2(registry_path, MIRROR / registry_path.name)
                    print(f'OK {scene_id}: {target.stat().st_size} bytes', flush=True)
                    return
                except Exception as exc:
                    temp.unlink(missing_ok=True)
                    print(f'RETRY {scene_id} ({attempt + 1}/3): {type(exc).__name__}', flush=True)
                    if attempt < 2:
                        await asyncio.sleep(2 ** (attempt + 1))
            failures.append(scene_id)

    await asyncio.gather(*(render(scene, text) for scene, text in plan))
    if failures:
        raise SystemExit('Failed scenes (rerun to retry): ' + ', '.join(failures))
    print(f'DONE: {len(plan)} MP3s available in both web versions.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voice', choices=['vi-VN-HoaiMyNeural', 'vi-VN-NamMinhNeural'], default='vi-VN-HoaiMyNeural')
    parser.add_argument('--rate', default='-8%')
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--jobs', type=int, choices=[1, 2, 3], default=2)
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    options = parser.parse_args()
    if options.start < 0 or options.limit < 0:
        parser.error('--start and --limit must be non-negative')
    asyncio.run(generate(options))
