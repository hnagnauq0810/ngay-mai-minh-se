"""Read the active, fully prepared narration profile used for static publishing."""
import json
from pathlib import Path
import re


def load_profile(root: Path):
    profile=json.loads((root/'content/narration_profile.v1.json').read_text(encoding='utf-8'))
    if not re.fullmatch(r'voice-story(?:-[a-z0-9]+)*',profile.get('directory','')):
        raise ValueError('Invalid narration directory')
    if not profile.get('voice'):
        raise ValueError('Narration voice name is required')
    return profile
