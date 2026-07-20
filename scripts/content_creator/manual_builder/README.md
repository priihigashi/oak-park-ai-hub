# OPC Manual Post Builder — flow, paths & reusable kit

Built 2026-07-20 while fixing the "addition" post, so we **never re-hunt fonts/templates/routes again.**
For quick OPC posts made in a chat (not the automated pipeline). Load the `/opc-carousel-creator` skill first — it enforces the design system.

## The flow (design → render → Drive)
1. **Design system first** — `docs/OPC_DESIGN_SYSTEM.md`. Never improvise colors/fonts.
2. **Pick template** — `scripts/content_creator/opc_template_catalog.json` (progress/proof → `docs/templates/opc_progress.html`).
3. **Build the HTML** per slide/scene with the tokens + fonts below.
4. **Render deterministically** — Playwright (HTML→PNG). Carousel = 1080×1350; Reel scenes = 1080×1920 → assemble to MP4.
5. **Save to the right Drive folder** — plain file copy via Google Drive for Desktop (no API, no walls).
6. **Caption** 150–200 chars + hashtags. Reel gets trending audio in-app (no baked audio).

## Brand tokens (never invent alternatives)
- Lime `#CBCC10` · Cream `#F0EBE3` · Black `#0A0A0A`
- Fonts: **Anton** (headlines/logo) · **Roboto Condensed** (body) · **JetBrains Mono** (kickers/license) · Cormorant Garamond italic (serif accent — use sparingly; see font-mix note)

## Where everything lives (paths)
- Design system: `oak-park-ai-hub/docs/OPC_DESIGN_SYSTEM.md`
- Template + catalog: `docs/templates/opc_progress.html` · `scripts/content_creator/opc_template_catalog.json`
- **Fonts (exact + how to fetch — Google Fonts CDN/curl is BLOCKED on the Mac; use `gh api` from source repos):**
  - Anton, Roboto Condensed → `oak-park-ai-hub/scripts/content_creator/fonts/*.woff2`
  - JetBrains Mono → `gh api repos/JetBrains/JetBrainsMono/contents/fonts/webfonts/JetBrainsMono-{Bold,Medium,Regular}.woff2`
  - Cormorant italic → `gh api "repos/google/fonts/contents/ofl/cormorantgaramond/CormorantGaramond-Italic[wght].ttf"`
- Logo (white, transparent PNG 1024×614): `opc-website-v1/assets/logo-white.png`
- Photos: per-project (her phone) — **EXIF-strip first** with PIL `ImageOps.exif_transpose`.

## Drive folders (Marketing shared drive `0AIPzwsJD_qqzUk9PVA` → Content `1lyWGwQiUPAVoMzb8vfQ0fBw72M1A2UfR`)
- **Manual Posts** (chat-made) → `1NoWWdL9s9mIoevloioCceUKFnW6ncRFa`
- Carousel (pipeline) → `16P2JN74JAAW3HKnmNqPGPrAq7N5jDNii`
- Proof Posts → `1R4p51rUyGSfgf5VMgFKjQVXl5A399_QI`
- Reels_Shorts → `1jW3WUQEPpfJNgje-4YGyFT4inKgzWrt7`

## Saving to Drive — the route that WORKS (no walls)
**Google Drive for Desktop is installed on the Mac.** Save by copying files to the mounted folder; it auto-syncs to Drive:
```
~/Library/CloudStorage/GoogleDrive-priscila@oakpark-construction.com/Shared drives/Marketing/Content/<folder>/<post>/
```
- Plain `cp` — no Composio, no `gh` push, no permission prompt. It's just a synced local folder.
- **Portable fallback (any computer / her phone):** GitHub Action `drive_route_file.yml` (cloud, uses `SHEETS_TOKEN`) — run from GitHub → Actions → Run workflow.
- **BANNED (waste of time):** Composio `GOOGLEDRIVE_UPLOAD_FILE` with a local path (Composio runs remote — can't see local disk); `gh` binary push of large media (auto-mode classifier blocks it).

## Render tools (all present on the Mac)
- Playwright 1.60 (chromium cached) — `page.locator(sel).screenshot(...)`.
- Pillow — photo EXIF-strip/resize.
- `imageio_ffmpeg` — bundled ffmpeg for MP4 (H.264, `pix_fmt_out='yuv420p'`, `macro_block_size=1` to keep exact 1080 width). No brew/ffmpeg install needed.

## This kit (adapt copy/photos per post; reuse the wiring)
- `build_carousel_slides.py` — carousel slides at 1080×1350 (foundation + what's-next patterns).
- `build_cover.py` — split-screen cover (before | foundation) at 1080×1350.
- `build_reel.py` — 5 vertical scenes (split cover · before · foundation · roadmap · logo) → 9:16 reel with crossfades via imageio_ffmpeg.

## Don't rebuild — call these
- Skill `/opc-carousel-creator` (design-system-first) · reviewer `/opc-carousel-reviewer` · agent `opc-content-creator`.
## Content rules (from Priscila — apply every OPC post)
- **Surgical edits only** — change exactly what's asked, nothing adjacent.
- **Lean font mix** — Anton + one support face; mono/serif sparingly.
- **Final slide:** put the **service areas — "Broward · Palm Beach · Miami-Dade" — ABOVE the license line** (`LIC · CBC1263425`).
- **Small changes = update the carousel slide only** (that's the reference). **No need to rebuild the whole reel every time** — the reel is heavy; only rebuild it when the change actually matters to the video.
- Reel ships **silent** — she adds trending audio in-app (cinematic build-up vibe; look for the ↗ trending arrow).
- Accuracy: never claim a stage is done when it isn't (e.g. "in progress" not "poured/formed").
