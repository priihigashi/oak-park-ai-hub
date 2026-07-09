# Content Creator Rebuild — Phase 1 vs Phase 2 Decision Brief
**Date:** 2026-07-09 | **Status:** Decision ready | **Drafted by:** Daily Advancer

---

## Context

The Content Creator pipeline (`scripts/content_creator/main.py` + `content_creator.yml`) is the core daily carousel production system. It reads `routing.py::get_route(niche)` and writes to the niche-specific carousel folder. A rebuild has been discussed in two phases:

- **Phase 1:** Infrastructure hardening — error handling, failure logging to `🚨 Pipeline Failures` tab, Drive write verification, motion-default enforcement, visual-every-other-slide audit
- **Phase 2:** Wealth/Power deck prototype — new carousel format using the 7-stage story-flow method (hook → tension → stakes → turning point → evidence → resolution → CTA), targeting Brazil niche first

---

## Current State Assessment

**What's working:**
- `main.py` correctly resolves niche → `carousel_folder_id` via `routing.py` at runtime (no hardcoded IDs)
- Write shape (`v<N>_<slug>/{cover.html, png/, motion/, resources/}`) is correct per CLAUDE.md
- `opc_media_sorter.py` + `opc_media_sorter.yml` now in repo (committed 2026-07-06)

**Known gaps (from carousel_reviewer.py audit 2026-05-05):**
- Image validation paths not traced across both local-build AND Drive paths
- Auto-fix mode (`FIX_MODE=analyze_and_fix`) not wired to `auto_fix_drive_folder()`
- Pillow dependency not gated with warning/fallback
- No fallback for legacy subfolder layouts

**Content backlog:**
- Brazil niche has approved topics queued but no new carousel produced since content automation pause (June 2026)
- OPC niche: Mike talking-head scripts ready via 4AM agent (Vera), no production run in ~2 weeks

---

## Recommendation: Phase 1 First — Tight Scope, 1 Session

**Do Phase 1 before Phase 2.** Reason: Phase 2 (Wealth/Power deck) will hit the same Drive write and motion-default bugs as the current pipeline. Building the new format on top of a broken foundation means debugging two things at once.

**Phase 1 scope (1 focused session):**
1. Trace both execution paths in `carousel_reviewer.py` (local-build + Drive) — fix the 4 gaps from CODE FIX AUDIT checklist in CLAUDE.md
2. Verify `log_pipeline_failure()` is called on every exception in `content_creator.yml`
3. Confirm `motion/` directory is always populated before email preview fires
4. Add Pillow + ffmpeg dependency check with clear error message
5. Run one dry-run carousel for OPC niche (Talking Head format) end-to-end and verify Drive path

**Phase 1 success check:** One OPC carousel produced, Drive path verified, `🚨 Pipeline Failures` tab shows no new unresolved rows.

---

## Phase 2 Spec (after Phase 1 green)

**Format:** Wealth/Power deck — Brazil niche, 7-stage story-flow
- Slide 1: Hook (tension-first headline + face of named person per NAMED-PERSON RULE)
- Slide 2: Context (what's happening + stakes number)
- Slide 3: Who decided this (bio-grid, 2 people max)
- Slide 4: Turning point (what changed / the reveal)
- Slide 5: Evidence (data slide — 2-3 hard numbers)
- Slide 6: Resolution (what this means for you)
- Slide 7: CTA + source

**Motion:** Default ON (MP4 + GIF per MOTION IS DEFAULT ON rule)
**Visual rule:** Every slide has a visual anchor — no consecutive text-only slides
**First episode target:** Brazil → pending next approved topic from Content Queue

---

## Action Items Generated

| # | Item | Owner | Priority |
|---|------|-------|----------|
| 1 | Fix 4 carousel_reviewer.py audit gaps | Claude (1 session) | HIGH — blocks Phase 2 |
| 2 | Run OPC talking-head dry-run end-to-end | Claude | HIGH |
| 3 | Draft Wealth/Power deck HTML template | Claude | MEDIUM — after Phase 1 |
| 4 | Pick first Brazil Wealth/Power topic from Content Queue | Priscila | MEDIUM |

---
_Append this content to Productivity & Routine doc `1wVBuNOuOufT8WP4KCrrlVbKWRmQZjKvqmia1soUEBZE` once Composio googledocs connection is re-established._
