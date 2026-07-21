# OPC Design System — Source of Truth for All Oak Park Construction Content

**Read this FIRST before creating ANY OPC post, carousel, reel cover, or graphic. No exceptions.**
Last updated: 2026-07-16 · Maintained in `priihigashi/oak-park-ai-hub/docs/OPC_DESIGN_SYSTEM.md`

## Brand tokens (verified — never invent alternatives)
| Token | Value | Use |
|---|---|---|
| Obsidian black | `#0A0A0A` | primary dark background (website vars: `#1b1a13`/`#141309`) |
| **Signature lime** | `#CBCC10` | THE OPC accent — numbers, accents, brackets, highlights (darker `#9A9B0C`, lighter `#E4E66A`) |
| Cream / paper | `#F0EBE3` | light background + light-on-dark type (`#F2ECE0` variant) |
| Muted gray | `#7A7267` / `#8A7E68` | secondary text |
Any other hex in an OPC deliverable = **FAIL** (template-defined derived shades excepted).

## Fonts (exact stack + where the files live)
| Role | Font | Notes |
|---|---|---|
| Headlines / big numbers / logo | **Anton** | uppercase, line-height 0.9-0.98, letter-spacing -0.01em |
| Body copy | **Roboto Condensed** | 400 body, 700 emphasis |
| Kickers / tags / labels / license | **JetBrains Mono** | uppercase, letter-spacing 0.15-0.22em |
| Serif accent (editorial/dark) | Playfair Display 900 · Cormorant Garamond italic 300 | pull-quotes only |
WOFF2 files: `scripts/content_creator/fonts/` (Anton-Regular, RobotoCondensed Regular/Bold/Light). Web tokens: `opc-website-v1/assets/css/opc-shared.css`.

## Canvas + layout rules (non-negotiable)
- **1080 × 1350** (IG 4:5 portrait) · safe inset **108px** all sides
- **Corner brackets**: 4 corners, 28×28px, 2px solid lime, inset 40px
- Every content slide footer: `SWIPE →` + `Oak Park · CBC1263425`
- Final slide: `@oakparkconstruction` + `LIC · CBC1263425` — the **license number is a required brand element**
- Portrait photos only; cover headlines get text-shadow readability guard
- Visual cadence: never 3 consecutive text-only slides

## Approved templates (never invent a layout — pick from here)
Registry: `docs/templates/template_registry.json` · catalog w/ good_for/bad_for: `scripts/content_creator/opc_template_catalog.json` · shared CSS: `scripts/content_creator/opc_standalones.css`, `opc_tip_base.css`
| Template | Purpose | Good for |
|---|---|---|
| `opc_progress.html` (+ `opc_progress_media`) | **proof** | before/after, project showcase, field update — 3 variants: v1 dark / v2 cream / v3 lime-on-dark; has before/after split-panel component |
| `opc_tip.html` | 5-slide Tip of the Week (pipeline key `tip`; ⚠️ NOT registered in CONTENT_FORMATS — the registry's FORMAT-010 is a Brazil format; don't use FORMAT-010 for OPC tips until reconciled) | product/education tips |
| `opc_base.html` | dark hero cover | covers |
| `opc_statement.html` | quote/myth | contrarian statements |
| `opc_four_card_grid.html` | X-vs-Y compare | comparisons |
| `opc_item_spotlight.html` | single product | product features |
| `opc_material_profile.html` | dark material education | materials |
| `opc_duotone.html` | contrarian/myth | myth-busting |

## Slide structure spines
- **Progress/Proof (before-after)**: cover → stage → done (use split-panel for before/after) → what's next → credits
- **Tip (pipeline key `tip`)**: hook (<10 words, 1 of 5 hook types) → cost/stat (one big number) → teach/list (name the mistake explicitly) → apply (Mike's first-person voice) → sources + save-CTA

## Copy rules
Plain contractor voice (Mike's voice for tips) · no promises, no fake stats, no invented names/addresses/dates/crew · hook <10 words · caption 150-200 chars + hashtags (max 30).

## Rendering (deterministic only)
HTML → PNG via **Playwright/headless Chromium** (`python3 -m playwright`, installed on the Mac 2026-07-16; pipeline uses `export_slides.js` in Actions). **NEVER text-to-image AI for layouts** (OpenAI/Ideogram/Canva AI/etc. hallucinate the design). Photo EXIF/GPS must be stripped before any upload (PIL re-save).

## Folder routing (Drive, Marketing shared drive → Content `1lyWGwQiUPAVoMzb8vfQ0fBw72M1A2UfR`)
| Folder | ID | What goes there |
|---|---|---|
| Carousel | `16P2JN74JAAW3HKnmNqPGPrAq7N5jDNii` | automated pipeline output (`vN_<topic-slug>/`) |
| **Proof Posts** | `1R4p51rUyGSfgf5VMgFKjQVXl5A399_QI` | real-project photo posts — naming `vN_proof-<slug>/` w/ subfolders html/png/enhanced/originals_used/review |
| Manual Posts | `1NoWWdL9s9mIoevloioCceUKFnW6ncRFa` | quick manual chat-created posts |
| Reels_Shorts | `1jW3WUQEPpfJNgje-4YGyFT4inKgzWrt7` | video |

## Category decision tree (her 3 OPC categories)
1. **Talking Head / Expert** → Mike video <1 min (4AM agent finds topic) — video pipeline, not this doc
2. **Project Progress / Before-After** (min 4 photos, or 2 for before/after only) → `opc_progress.html`, Proof Posts folder
3. **Product Tips** (single image or carousel) → `opc_tip.html` spine, Carousel folder

## Related sources (read in this order when creating)
1. This doc  2. `opc_template_catalog.json` (pick template)  3. CONTENT_FORMATS Drive doc `1XqXSyJC_iHMTrmMxpM5ZR7S-WQxz19HhDJO1HomdncM` (format match)  4. Prior builds in the target Drive folder (version numbering)
Also: `PIPELINE_REGISTRY.md` (active templates map) · `skills/shared/template-carousel/SKILL.md` · `IMAGE_QUALITY_RULES.md` (photo sourcing cascade; named-person face rule).

## Before/After Proof Post — Full Build Guide (3 variants)

Use this guide every time a real project proof post is needed. Requires a human to provide the source photos first.

### Photo requirements
- Minimum 4 project photos (before × 1–2, during × 1, after × 1–2) — or exactly 2 for a pure before/after cover with no stage slide
- Source folder in Drive: `Proof Posts/vN_proof-<slug>/originals_used/`
- Strip EXIF/GPS before upload: `PIL.Image.open(path).save(path)` (re-save = strip)
- Portrait orientation required; landscape crops must be re-cropped to 4:5 before use

### Slide structure for proof posts (5-slide spine)
1. **Cover** — hook headline (<10 words), hero after-photo full-bleed
2. **Stage / challenge** — what the job was, one key stat or scope detail
3. **Done** — before/after split-panel (`opc_progress.html` split-panel component) — most impactful slide
4. **What's next / CTA** — short copy + save prompt
5. **Credits** — `@oakparkconstruction · LIC # CBC1263425`

### 3 mandatory variants (render all 3, Priscila picks one)
| Variant | Template call | Background | Accent | When to use |
|---|---|---|---|---|
| v1 dark | `opc_progress.html?variant=dark` | `#0A0A0A` obsidian | lime `#CBCC10` brackets + numbers | dramatic interiors, night shots, high-contrast projects |
| v2 cream | `opc_progress.html?variant=cream` | `#F0EBE3` cream | obsidian type + lime accent | bright exteriors, pool/patio, daytime light |
| v3 lime-on-dark | `opc_progress.html?variant=lime` | `#0A0A0A` + large lime headline block | cream body type | bold statement, stucco/concrete color work |

### Rendering steps (deterministic only — no AI image generation)
1. Confirm source photos are in `originals_used/` subfolder and EXIF-stripped
2. Run `export_slides.js` via GitHub Actions (`workflow_dispatch`) or local Playwright:
   `node export_slides.js --template opc_progress.html --variant dark,cream,lime --out vN_proof-<slug>/png/`
3. Output PNGs go to Drive `Proof Posts/vN_proof-<slug>/png/`
4. DO NOT share/schedule any PNG without Priscila visual review first
5. Enhanced edits (if any): `enhanced/` subfolder; originals stay in `png/`

### Naming convention
`proof-<project-slug>-v<N>-<variant>.png` — e.g. `proof-stucco-miami-v1-dark.png`

### After review
- Approved variant → move to `Manual Posts/` or schedule via Buffer
- Caption: 150–200 chars + up to 30 hashtags; Mike's first-person voice; no invented details

## Agent + skill references
- Claude agent definition: `claude-config/agents/opc-content-creator.md` (copy to `~/.claude/agents/` to activate)
- OPC carousel creator skill: `skills/shared/opc-carousel-creator/`
- OPC carousel reviewer skill: `skills/shared/opc-carousel-reviewer/`
- Codex awareness: `AGENTS.md` in repo root (Codex reads this at every session start)

## Never do this again (real failures)
- **2026-07-16 navy/orange incident**: a session invented a navy `#102A43` / orange `#E87722` "brand" from nothing instead of reading this system. Rejected on sight. If you don't know the brand — STOP and read this doc; never improvise colors.
- Don't ship dashed "PHOTO" placeholder slots in a real post — fill every image slot or remove the slide.
- Don't fabricate crew names, project IDs, street addresses, or dates to fill template sample fields.
- **Before any 3-variant render**: confirm real source photos exist in `originals_used/` — never ship a render with placeholder images as a deliverable for Priscila to review.
- **A fresh session must load this doc first** — do not skip directly to rendering or template editing without reading the brand tokens and template list above.
- **Do not publish/upload without Priscila approval** — even after a technically correct render, visual review is required. Render → share for review → approval → post.
- **Do not use FORMAT-010 for OPC tips** — FORMAT-010 is a Brazil niche format. OPC tips use `opc_tip.html` with the `tip` pipeline key; check CONTENT_FORMATS before assigning any FORMAT-ID to OPC content.

## Changelog
- 2026-07-21 (daily-advancer): added Before/After Proof Post full build guide (photo requirements, 3-variant table, render steps, naming convention, after-review flow), agent/skill references, and 4 new bad-output blockers based on 2026-07-17 audit flags.
- 2026-07-16 (validation): fresh-session test PASSED — agent given only "make a tip carousel about rebar" self-loaded skill → design system → catalog → template → CONTENT_FORMATS → prior builds, produced on-brand prep, zero drift. Flags it raised: FORMAT-010 numbering conflict (fixed above), topic overlap with `v1_foundation-reinforcement...` (bump slug at build time).
- 2026-07-16: created from live audit (repo templates + opc-website tokens + Drive folder mapping). First consumer: addition before/after post (3 variants rendered from opc_progress).
