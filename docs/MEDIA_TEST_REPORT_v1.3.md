# Media implementation QA — v1.3 (04/11/2026)

> Báo cáo bên dưới mô tả gói source gốc, trước bản sửa âm thanh/ảnh. Trạng thái mới: đã tải 29 ảnh, tích hợp MP3 tiếng Việt và rà đủ 55 cảnh. Xem [AUDIO_MEDIA_FIX_REPORT.md](AUDIO_MEDIA_FIX_REPORT.md) và [media_story_review.csv](media_story_review.csv).

## Scope

- 23 Commons image records with `source_url`, intended date, described event, photographer/creator and license declared on the file page.
- Media mapped to 55/55 story scenes and the 14 opening/closing sections; all scenes render `<figure>` + caption + source link.
- Cinema mode updates the scene's photograph and citation as the continuous narrator advances.
- An optional archival film link is displayed for the Geneva 1954 segment (C07_S01). Playback is external and intentionally not automatically streamed in the Cinema Player.
- Images labelled `archive` vs `contemporary`; later photographs of museums are not presented as wartime photographs.
- `scripts/download_commons_media.py` can localize images and `scripts/export_video.py` uses them when available.

## Automated checks

- `python scripts/build_site.py`: PASS (55 scenes generated)
- `python scripts/validate_content.py`: PASS (12 chapters / 55 scenes)
- `python scripts/validate_media.py`: PASS (23 image references / 55 scene assignments)
- `node --check public/assets/cinema.js`: PASS
- `node --check public/assets/site.js`: PASS
- `python tests/cinema_smoke.py`: PASS (1440 × 900, 390 × 844, next/pause/resume/stop)
- `python tests/e2e_smoke.py`: PASS (1440 × 900, 390 × 844). Test deliberately blocks outbound HTTPS for deterministic UI testing; this does **not** verify remote image loading.

## Known limitations / release gate

- **The ZIP does not contain JPEG originals**. The build references Commons online. A dev machine with Internet can run `python scripts/download_commons_media.py --all`, then `python scripts/build_site.py` to bundle image files locally.
- Network access to the Wikimedia image CDN could not be verified from this execution environment. Before release, browse every image once or run the downloader and manually inspect.
- Commons licensing and historical descriptions shown here are attribution metadata under review; final rights clearance and history review are required. Some historical stills have complex provenance.
- Some photos intentionally repeat across neighboring scenes where distinct source material could not be corroborated. Do not fabricate images of events to fill these gaps.
- The 1954 archival film is an optional external link, not a video silently injected into an uninterrupted narrated film.
- Real Vietnamese narrator MP3s remain an independent optional build step using the user's approved TTS key; demo voice depends on the available Vietnamese OS/browser TTS voices.
