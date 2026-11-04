# Test report v1.2 — continuous cinema

- Content schema/ids: PASS — 12 chapters, 55 scenes.
- JS syntax check (`node --check public/assets/cinema.js`): PASS.
- Chromium desktop 1440×900: PASS — start, pause, resume preserving audio playback time, ended event advances to next scene, manual next, loop scene 55→1, stop, close, no JS page errors.
- Chromium mobile 390×844: PASS — same test cases.
- FPT TTS API build script: local dry-run PASS — 55 request blocks default and 164 request blocks dramatized; no real FPT request was possible (no API key/network).
- Audio multi-voice concatenation via ffmpeg: PASS using synthetic placeholder tracks.
- MP4 exporter: PASS one-scene smoke using synthetic silent audio. Full 55-scene MP4 not produced (no licensed narration tracks).
- Next.js build: NOT TESTED — npm registry not accessible in this environment. Frontend assets run independently via standalone mode.
- Historical review and media-rights release gate: NOT APPROVED — must be completed before public release.
