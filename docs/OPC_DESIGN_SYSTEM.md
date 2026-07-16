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

## Never do this again (real failures)
- **2026-07-16 navy/orange incident**: a session invented a navy `#102A43` / orange `#E87722` "brand" from nothing instead of reading this system. Rejected on sight. If you don't know the brand — STOP and read this doc; never improvise colors.
- Don't ship dashed "PHOTO" placeholder slots in a real post — fill every image slot or remove the slide.
- Don't fabricate crew names, project IDs, street addresses, or dates to fill template sample fields.

## Changelog
- 2026-07-16 (validation): fresh-session test PASSED — agent given only "make a tip carousel about rebar" self-loaded skill → design system → catalog → template → CONTENT_FORMATS → prior builds, produced on-brand prep, zero drift. Flags it raised: FORMAT-010 numbering conflict (fixed above), topic overlap with `v1_foundation-reinforcement...` (bump slug at build time).
- 2026-07-16: created from live audit (repo templates + opc-website tokens + Drive folder mapping). First consumer: addition before/after post (3 variants rendered from opc_progress).
