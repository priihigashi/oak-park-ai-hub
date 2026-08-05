# Content Creator V2 — Dependency Inventory

Date: 2026-08-05
Runtime code changed: no.

## Existing observed dependencies / services

| Dependency / service | Seen in repo | Current use | V2 decision |
|---|---|---|---:|
| Python | yes | capture/content pipeline scripts | REUSE |
| Google Drive API | yes | uploads, file access, shared drives | REUSE + GUARD |
| Google Sheets API | yes | trackers/catalogs/queues | REUSE + GUARD |
| Gmail API / SMTP / GitHub Action email | yes | preview/approval/alerts | REUSE |
| GitHub Actions | yes | scheduled/triggered workflows | REUSE |
| `routing.py` | yes | canonical per-niche destinations | REUSE + EXTEND |
| Whisper API | yes | capture transcription | REUSE |
| Claude / OpenAI / Gemini cascade patterns | yes | analysis/classification/fallbacks | REUSE + GUARD |
| Apify | yes | Instagram metadata | REUSE where needed |
| yt-dlp | yes | media/audio extraction | REUSE |
| Playwright | yes in docs/manual pattern | HTML to PNG | REUSE |
| Pillow | yes | image processing/EXIF handling | REUSE |
| imageio_ffmpeg | yes in manual docs | MP4 assembly | REUSE |
| Buffer API | yes | scheduling after approval | DO NOT TOUCH YET |
| Remotion | referenced/legacy/frozen | renderer/motion | DO NOT TOUCH YET |
| GIPHY | yes in motion sources | fallback source | REPLACE LATER / keep only if proven useful |
| Pexels/Pixabay legacy | retired in rules | old source cascade | DO NOT RE-ADD |

## Candidate additions to evaluate later

| Candidate | Purpose | When to add | Decision |
|---|---|---|---:|
| PySceneDetect | scene segmentation and representative frames | Package 1 after schema tests | REUSE |
| osxphotos | Apple Photos export with JSON/XMP sidecars | Package 1 local prototype | REUSE |
| OpenCLIP / CLIP-compatible local model | semantic frame/image search | Package 1/2 after M3 8GB test | REUSE / ADAPT |
| SQLite | local asset index | Package 1 | REUSE |
| sqlite-vec / FAISS / Chroma | vector search | only after simple SQLite index is proven insufficient | REPLACE LATER |
| WhisperX | word-level timestamps | when transcript timing/caption precision becomes blocker | EXTEND |
| jsonschema / pydantic | timeline/provenance schema validation | Package 0 | BUILD NEW |
| Remotion | final programmatic rendering | after timeline schema approved | DO NOT TOUCH YET |
| Electron/React timeline UI | visual approval interface | much later | REPLACE LATER |

## Dependency rules

### No personal media in Git

Never commit:

- real videos
- personal photos
- local cache
- embeddings
- derived thumbnails from private media
- exported private documents
- OAuth tokens
- API keys
- cookies
- secrets

### Local cache rules

Any future cache/index path must be:

- outside tracked Git paths
- covered by `.gitignore`
- safe to delete/rebuild
- documented as `SYSTEM` or `LOCAL_CACHE`, not canonical content storage

Suggested cache naming:

```text
~/Library/Application Support/JarvisAthena/content_creator_v2/
  indexes/
  proxies/
  thumbnails/
  transcripts/
  manifests/
```

Do not use backup/reset folders for cache or canonical output.

### Apple Photos rule

Do not depend on direct `Photos.sqlite` reads for production.

Use an export-driven path with metadata sidecars:

```text
Apple Photos export -> sidecar metadata -> local media index -> semantic search
```

### Model-size rule

Priscila's known machine target is a MacBook Air M3 8GB. Any local model dependency must be tested against that constraint before becoming mandatory.

### Three-tier fallbacks

Where external services exist, preserve the existing resilience principle:

1. best/reliable source
2. fallback source
3. offline/manual-review fallback

But do not create provider sprawl. V2 should prefer local/owned media first.

## Package 0 dependency changes

Allowed in Package 0:

- documentation
- JSON schemas
- schema fixtures
- schema tests

Not allowed in Package 0:

- new video/model dependencies
- media indexing against real personal media
- runtime orchestration changes
- Drive file moves
- Remotion integration
