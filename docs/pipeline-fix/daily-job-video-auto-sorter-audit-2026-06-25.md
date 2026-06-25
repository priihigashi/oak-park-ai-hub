# Daily Job-Video Auto-Sorter — Codex Audit + Corrected Build Plan

Date: 2026-06-25
Project: Oak Park Construction media automation
Repo: `priihigashi/oak-park-ai-hub`

## Verdict

Build it, but do not build it as a separate universe.

The pasted plan is directionally right about GitHub Actions, Drive OAuth, GPS/date metadata, and the daily-cron-first approach. The main correction is that the catalog sheet does already exist: `scripts/photo_catalog_cloud.py` writes to the Ideas & Inbox spreadsheet tab `📸 Photo Catalog` (`1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU`). The new sorter must extend that ecosystem instead of creating a new "OPC Media Catalog" by default.

## Existing Automation Inventory

Surfaces this touches:

- GitHub Actions
  - `.github/workflows/photo-catalog.yml` — existing daily photo catalog scan, runs in GitHub Actions, writes `SHEETS_TOKEN` to `/tmp/oak_park_creds/sheets_token.json`, calls `scripts/photo_catalog_cloud.py`.
  - `.github/workflows/drive_route_file.yml` — routes My Drive files to topic shared drives via `scripts/drive_route_file.py`.
- Scripts
  - `scripts/photo_catalog_cloud.py` — current cloud photo catalog + idea generator.
  - `scripts/drive_route_file.py` — Drive move pattern using `supportsAllDrives=True`.
  - `scripts/content_creator/photo_matcher.py` — reads `📸 Photo Catalog` downstream for real OPC photo matching.
- Spreadsheet
  - Ideas & Inbox: `1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU`
  - Existing tab: `📸 Photo Catalog`
- Secrets / env vars
  - `SHEETS_TOKEN`
  - `CLAUDE_KEY_4_CONTENT`
  - optionally no new secret for phase 1
- Drive
  - OPC shared drive: `0AJp3Phs0wIBOUk9PVA`
  - Pasted drop folder: `1dNmFflB0yS8Qc9A1-mfbMCIHOVZzcndb`
  - Pasted projects folder: `1t7bKvdaHCSQjiDeqtYQH7cG7mGoB3Bbu`

## Audit Of The Pasted Answer

### What is correct

- Running from GitHub Actions is the right model. It does not require Priscila's computer to be open.
- Using the existing OAuth pattern from `SHEETS_TOKEN` is correct.
- Daily cron plus manual `workflow_dispatch` is the safest phase 1 trigger.
- `ffprobe` is the right first tool for iPhone MOV metadata.
- GPS should stay enabled as a sorting signal. If metadata is missing, route to a review/no-location folder instead of failing.
- Moving within Drive by updating parents is the right approach, as long as every call includes `supportsAllDrives=True`.

### What needs correction

- The catalog was not missing. The existing target is Ideas & Inbox -> `📸 Photo Catalog`.
- The current catalog script is image-first only. It does not currently process videos.
- Current catalog idempotency is filename-based (`get_cataloged_filenames` reads column D). That is not safe enough for videos or repeated filenames. The sorter must record Drive file IDs.
- The current photo catalog workflow runs at `23:35 UTC` / about `7:35 PM ET`, not 5 AM ET.
- The existing catalog script logs errors to stdout and continues; it does not have a `Pipeline Failures` tab or guaranteed red Action behavior for per-file errors.
- The pasted "move is atomic; if log write fails the file ID is still recorded" is not true unless implemented with a durable processed-file ledger before/after move. It is a required design, not a current fact.
- "Date is always derivable" should be softened: Drive `createdTime` is always available, but it may be upload time, not capture time, if EXIF/QuickTime metadata was stripped.

## Decision

Build phase 1 as a sibling workflow/script, not as a rewrite of the current photo catalog:

- New script: `scripts/opc_media_sorter.py`
- New workflow: `.github/workflows/opc_media_sorter.yml`
- Reuse: `SHEETS_TOKEN` OAuth refresh pattern from `scripts/photo_catalog_cloud.py`
- Reuse target: Ideas & Inbox `📸 Photo Catalog`
- Add or use companion tabs:
  - `📸 Photo Catalog` for media rows
  - `📍 Project Registry` for project GPS anchors
  - `🚨 Pipeline Failures` for hard and soft failures
  - optional `🧾 Media Sort Ledger` if Drive file IDs do not fit cleanly in the catalog tab

Do not add reverse-geocoding in phase 1. GPS-to-known-project matching is cheaper, more private, and more useful.

## Improved Build Plan

### Phase 0 — Verify Drive IDs

Before coding, verify the pasted Drive IDs with the Drive API:

- `1dNmFflB0yS8Qc9A1-mfbMCIHOVZzcndb` is the intended drop folder.
- `1t7bKvdaHCSQjiDeqtYQH7cG7mGoB3Bbu` is the intended projects/media parent.
- Both live in the OPC shared drive `0AJp3Phs0wIBOUk9PVA`.

If any ID is wrong, stop and update this plan before implementation.

### Phase 1 — Daily Sorter

Workflow:

- Runs daily after the existing photo catalog run, or manually.
- Installs `ffmpeg` so `ffprobe` is available.
- Installs `google-auth`, `google-api-python-client`, and any metadata dependency chosen for images.
- Writes `SHEETS_TOKEN` to `/tmp/oak_park_creds/sheets_token.json`.
- Calls `python scripts/opc_media_sorter.py`.

Script behavior:

1. List files in the drop folder, with shared-drive flags on every Drive call.
2. Skip folders and already-processed Drive file IDs.
3. For each file:
   - read metadata date/time
   - read GPS if present
   - match GPS to Project Registry within the configured radius
   - create/find `YYYY-MM-DD/<ProjectName>` or `YYYY-MM-DD/_no-location`
   - move the file by parent update
   - append/update a catalog row with Drive file ID, links, date, project, media type, GPS, and status
4. On file-level metadata failure:
   - move to `YYYY-MM-DD/_needs-review` when possible
   - log to `🚨 Pipeline Failures`
   - continue unless the failure is auth/config/systemic
5. On auth/config/systemic failure:
   - log to `🚨 Pipeline Failures`
   - exit non-zero so GitHub Actions turns red.

### Phase 2 — Merge With Photo Catalog

After sorting is stable:

- Decide whether `photo_catalog_cloud.py` should scan sorted folders, the drop folder, or both.
- Change idempotency from filename to Drive file ID.
- Add video rows to `📸 Photo Catalog` with media type `video`.
- Keep content idea generation limited to client-visible/high-quality rows.

### Phase 3 — Optional Near-Real-Time Trigger

Only build this if daily sorting is too slow. Options:

- Google Apps Script folder watcher calling GitHub `workflow_dispatch`.
- Drive Activity polling.

This is intentionally later because it adds auth and maintenance complexity.

## Metadata Contract

For videos:

- Primary date: `com.apple.quicktime.creationdate`
- Fallback date: `creation_time`
- Final fallback: Drive `createdTime` with status note `date_source=drive_createdTime`
- GPS: `com.apple.quicktime.location.ISO6709`, parsed from values like `+26.1134-080.1951+003.952/`

For photos:

- Primary GPS/date: Drive `imageMediaMetadata` when available.
- Fallback: download and inspect EXIF if needed.
- Final fallback: Drive `createdTime`.

Never treat fallback upload time as the same quality as original capture time. Record `date_source` and `gps_source`.

## Catalog Schema Additions

Existing `📸 Photo Catalog` columns should be preserved. Add columns only if missing:

- Drive File ID
- Media Type
- Date Source
- GPS Source
- GPS Lat
- GPS Lon
- Sort Status
- Sorted Folder URL
- Original Parent ID
- Processed At

This keeps downstream scripts such as `scripts/content_creator/photo_matcher.py` compatible.

## Idempotency And Safety Requirements

Pass/fail requirements for Codex:

- Uses Drive file ID, not filename, as the processed identity.
- Does not duplicate rows on rerun.
- Does not re-move already sorted files on rerun.
- Uses `supportsAllDrives=True` on every get/list/create/update/delete/media call.
- Uses `includeItemsFromAllDrives=True` and `corpora="allDrives"` where listing/searching across shared drives.
- Never moves files into My Drive.
- Never overwrites a folder or file with the same name.
- Records enough state to recover if logging fails after a move.
- Has a dry-run mode before the first real move.

## Recommended Codex Prompt

```text
Audit and implement the Daily Job-Video Auto-Sorter in priihigashi/oak-park-ai-hub.

Read first:
- AGENTS.md
- CLAUDE.md
- docs/pipeline-fix/daily-job-video-auto-sorter-audit-2026-06-25.md
- scripts/photo_catalog_cloud.py
- .github/workflows/photo-catalog.yml
- scripts/drive_route_file.py

Do not create a separate catalog spreadsheet unless the existing Ideas & Inbox `📸 Photo Catalog` cannot support the required columns. Reuse the existing sheet ID `1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU`.

Build phase 1 only:
- `scripts/opc_media_sorter.py`
- `.github/workflows/opc_media_sorter.yml`
- dry-run mode
- shared-drive-safe Drive API calls
- file-ID idempotency
- date/GPS extraction for iPhone MOV via ffprobe
- no-GPS fallback to `_no-location`
- failure logging to `🚨 Pipeline Failures`
- append/update rows in `📸 Photo Catalog`

Before coding, verify the pasted folder IDs with Drive API. If they do not resolve to the OPC shared drive, stop and report the exact mismatch.

After coding, run unit tests for:
- GPS video route
- no-GPS video route
- stripped metadata route
- rerun/idempotency
- shared-drive move args
- log-failure nonzero behavior
```

## Open Items

- Confirm the drop folder ID is stable and meant for Mike's uploads.
- Confirm whether the target folder structure should be under the pasted Projects folder or under `Mikes Photos & Videos`.
- Pick the match radius. Default recommendation: 150 meters.
- Decide whether videos should generate content ideas immediately or only after human review.
