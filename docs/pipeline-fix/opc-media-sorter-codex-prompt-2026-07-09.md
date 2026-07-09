# CODEX TASK — OPC Daily Job-Video Auto-Sorter
**Added by Daily Advancer 2026-07-09**
**Based on audited build spec:** https://docs.google.com/document/d/1cSsxJ0NtrjrHKjPbrPdgyZCN6uJoc8D3hf-AvfkOQ2k/edit

## What to build
Two NEW files — do NOT modify any existing scripts:
- `scripts/opc_media_sorter.py`
- `.github/workflows/opc_media_sorter.yml`

---

## Step 0 — VERIFY Drive IDs BEFORE writing any code

Call Drive API (`supportsAllDrives=True`) to confirm every ID below exists inside OPC shared drive `0AJp3Phs0wIBOUk9PVA`. STOP and flag any ID that does not resolve — do not write file-operation code against an unverified ID.

| Role | Drive ID |
|---|---|
| Drop folder (parent) | `1dNmFflB0yS8Qc9A1-mfbMCIHOVZzcndb` |
| Projects folder | `1t7bKvdaHCSQjiDeqtYQH7cG7mGoB3Bbu` |
| New Construction folder | `1nYPQmO7xb1m_8EKo3E_QbSpoYfkbO1yJ` |
| Catalog sheet (Ideas & Inbox) | `1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU` |
| Catalog tab | `📸 Photo Catalog` |

---

## Authentication

Reuse the OAuth pattern from `scripts/phase1_scanner/scan_and_tag.py` (SHEETS_TOKEN / sheets_token.json). No new auth setup needed.

Rules that apply to EVERY Drive API call:
- `supportsAllDrives=True` on every call — missing this = 404 on shared drives
- `includeItemsFromAllDrives=True` on every `files().list()` call
- Never move a file to My Drive; moves must stay within the OPC shared drive

---

## Workflow file: `.github/workflows/opc_media_sorter.yml`

```yaml
name: OPC Media Sorter

on:
  schedule:
    - cron: '0 3 * * *'   # 3 AM UTC (~11 PM ET) — after photo_catalog_cloud.py cron (~7:35 PM ET)
                            # Codex: confirm exact existing cron time and adjust if needed to avoid collision
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Dry run — log what would move, move nothing'
        type: boolean
        default: false

jobs:
  sort:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install system deps
        run: sudo apt-get install -y ffmpeg
      - name: Install Python deps
        run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
      - name: Run sorter
        env:
          SHEETS_TOKEN: ${{ secrets.SHEETS_TOKEN }}
        run: python scripts/opc_media_sorter.py ${{ github.event.inputs.dry_run == 'true' && '--dry-run' || '' }}
```

---

## Script: `scripts/opc_media_sorter.py` — logic per file

### Pipeline (run for each unprocessed file in the drop folder)

1. **List files** in drop parent folder. Skip any file whose Drive FILE ID is already in the `📸 Photo Catalog` tab (strong dedup — NOT filename).

2. **Read capture date** — priority order:
   - `com.apple.quicktime.creationdate` (local time with timezone — most accurate)
   - `creation_time` from video metadata (UTC)
   - Drive `createdTime` (upload time — fallback of last resort)
   - When falling back to `createdTime`, set a flag: `date_source = "upload-time-only / not verified capture date"`
   - Date fallback must NEVER produce an empty or "unknown" folder name.

3. **Read GPS** — priority order:
   - `com.apple.quicktime.location.ISO6709` (video) — e.g., `+26.1134-080.1951+003.952/` → lat 26.1134, lon -80.1951
   - `imageMediaMetadata.location` from Drive API (photos/DNG — free, no extra download)
   - exiftool EXIF GPS tags (fallback for images)

4. **Create `YYYY-MM-DD` subfolder** in drop parent if it does not exist yet.

5. **Project matching** (GPS present):
   - Project Registry: each active job = name + one known (lat, lon), seeded from first geotagged photo in each project folder, with manual address fallback.
   - Match: nearest registered project within 150 m.
   - Match found → move file to `YYYY-MM-DD/ProjectName/`
   - No match (or no GPS) → move to `YYYY-MM-DD/_no-location/_needs-review`
   - Nothing stays in the drop root; nothing is deleted.

6. **Move** (not copy) the file within the OPC shared drive — `update(fileId, addParents, removeParents)`.
   - Name collision in target folder: append suffix (`IMG_0001_2.MOV`), NEVER overwrite.

7. **Log row** to `📸 Photo Catalog` tab — see column spec below.

8. **On any error**: call `log_pipeline_failure(stage, error)` to `🚨 Pipeline Failures` tab in the same spreadsheet, then `sys.exit(1)` so the GitHub Action flips red. This is NOT optional — build it, do not assume it exists.

---

## Catalog columns — add without breaking `photo_catalog_cloud.py`

`photo_catalog_cloud.py` ignores unknown columns, so appending new columns is safe. Add:

| Column header | Values |
|---|---|
| `File ID` | Drive file ID (string) |
| `Media Type` | `video` or `photo` |
| `GPS lat,lon` | e.g., `26.1134,-80.1951` or blank |
| `Day Folder Link` | Drive URL of the `YYYY-MM-DD` subfolder |
| `Status` | `sorted` / `no-location` / `needs-review` |

---

## Division of labor — CRITICAL, do not change

| Script | Scope |
|---|---|
| `photo_catalog_cloud.py` | Catalogs **images** from already-sorted **project folders** |
| `opc_media_sorter.py` | Sorts and catalogs **videos only** from the **drop folder** |

The new sorter must NOT catalog images. The existing script must NOT be modified.

---

## Idempotency requirements

- Dedup by Drive FILE ID — not filename. `IMG_0001.MOV` from Job A vs Job B are different files.
- Re-running on the same input must produce no double-logs and no re-moves.
- If the catalog log write fails after a successful move: the file ID is in Drive's new location. Record it as `"moved, log-write-failed"` in a local state so the next run skips the move and retries only the log.

---

## Pre-ship audit checklist (verify all before marking this task done)

- [ ] Step 0: every Drive ID verified against OPC shared drive before any file-operation code ran
- [ ] File with GPS → sorted into correct project subfolder
- [ ] File without GPS → lands in `_no-location/_needs-review`, NOT left in drop root
- [ ] Re-run on same input: 0 double-logs, 0 re-moves
- [ ] All Drive API calls use `supportsAllDrives=True`
- [ ] Failure logging: `sys.exit(1)` fires on any exception → Action turns red
- [ ] Date fallback: `createdTime` fallback produces a valid `YYYY-MM-DD` folder, never empty
- [ ] Sorter cron confirmed to NOT collide with `photo_catalog_cloud.py` cron
- [ ] Dry-run mode: logs intended moves, makes zero Drive writes

---

## Key background for Codex

- Mike uploads originals straight from the Photos app to the drop folder. Direct uploads keep capture date + GPS.
- WhatsApp/iMessage sharing strips both — this is documented; only Priscila needs to remind Mike, no code change needed.
- Drop folder name for Mike's reference: "Daily Job Videos - DROP HERE (Mike)"
