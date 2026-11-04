# Implementation Notes — Code Release 1.0

## Engineering decisions versus handoff HLD

This working implementation has **the same product scope** but consolidates the 55 scenes into **one long, server-rendered document**, instead of one separate route per chapter. Every chapter is reachable by a stable `/#chuong-07` anchor, and every scene by `/#C07_S03`. This keeps continuous cinematic flow and works in static hosting without per-route JS hydration.

It also uses **native IntersectionObserver + CSS transitions** rather than GSAP. This is an intentional simplification: no animation package or browser scroll-scrubbing overhead for a text-first experience. The motion is optional, reduced-motion is respected, and the content remains readable without JS.

The content renderer is **source-generated accessible HTML**, consumed by both Next.js (server/static export) and the dependency-free standalone site. This is a deliberate lightweight architectural tradeoff versus creating separate React components for each scene. The static site remains functional if npm dependencies are unavailable.

## Architecture

```
content/story_manifest.v1.json + chapters.v1.json
                         |
                 scripts/build_site.py
                         |
             generated/pageMarkup.json
                  /              \
         Next.js app/page      standalone/index.html
                  \              /
              shared site.css + site.js
                         |
             Cloudflare Pages / Netlify / any CDN
```

No backend, database, server actions, account, auth, analytics or message submission in Release 1.

## Functions implemented

- 55 fully written scenes in script order, prologue, 12 chapters, epilogue.
- `#C07_S03` scene links, `#chuong-07` chapter links, persistent sticky progress.
- Chapter navigation drawer with keyboard focus trapping and Escape closing.
- 1954–1975 responsive North/South split-screen context on scenes 07 and 08.
- User-initiated Vietnamese browser speech synthesis of historical narrator text; no voice cloning. Voice availability depends on OS/browser.
- Read mode, reading fallback, copy scene, local-only reflection, responsive visuals.
- Art direction using original vector drawings, *not* allegedly archival photos.
- Repeated visible labels marking fictional dialogue and content in draft review.
- Static-safe deployment and strict separate release review gate.

## Known constraints

- Source texts are **draft**. Claim registry and source mapping have not been signed off.
- No historically sourced photo/video/audio assets were provided; original SVG illustrations used instead. Voice is OS-level browser speech, not a professionally recorded narration track.
- `npm run build` requires internet access to install Next dependencies on a new machine. Standalone preview has zero dependencies and can be tested here.
- For production, verify dates/claims and captions against primary sources, clear media rights, check WCAG with screen-reader testing, and perform real-device performance audit.
- Layout and JS cover full content but final art direction, recorded voice and content-specific media require content production.

## Release policy

`npm run validate` passes while content is in draft; `npm run test:release` is **expected to fail** until claim/source registries, verified statuses, copyright approvals and historian sign-off are complete. Never remove the warning banner or set robots indexing true before approval.
