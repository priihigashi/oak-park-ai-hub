# Carousel Reviewer — Phase 1 Gap Audit
Daily Advancer — 2026-07-29

Reference: docs/content-creator/rebuild-phase-decision-2026-07-09.md listed 4 gaps in
carousel_reviewer.py as Phase 1 blockers before Phase 2 (Wealth/Power deck) can begin.

This audit verifies the current state of each gap in the live file
(scripts/content_creator/carousel_reviewer.py).

---

## Verdict: ALL 4 PHASE 1 GAPS ARE ALREADY FIXED

Phase 1 prerequisite work is DONE. Phase 2 is unblocked from the carousel reviewer side.

---

## Gap-by-gap findings

GAP 1 — Image validation paths not traced across both local-build AND Drive paths
Status: FIXED
Evidence:
- `_patch_html_placeholders()` (line ~635) includes explicit "Path A (local)" and "Path B (Drive)"
  comments and handles both execution paths.
- `_rerender_and_upload()` (line ~738) also documents "Runs on BOTH execution paths."
- `check_resource_images_local()` (line ~1394) handles the local build path.
- `_check_image_relevance_drive()` (line ~1462) handles the Drive review path.
Both paths are fully traced and handled.

GAP 2 — Auto-fix mode (FIX_MODE=analyze_and_fix) not wired to auto_fix_drive_folder()
Status: FIXED
Evidence:
- Line 1700: `if FIX_MODE == "analyze_and_fix" and (has_regen or has_text_issues) and not DRY_RUN:`
  → calls `auto_fix_drive_folder()` via lazy import from `auto_fixer` module.
- Line 2736: Same pattern repeated for the Drive review path.
FIX_MODE gating is properly wired in both the local-build and Drive-review code branches.

GAP 3 — Pillow dependency not gated with warning/fallback
Status: FIXED
Evidence:
- Lines 41-44:
    try:
        from PIL import Image, ImageStat
    except Exception:
        Image = None
        ImageStat = None
- Lines 539, 888, 1407, 1515: All Pillow usage is guarded with `if Image is not None`.
The fallback is clean — missing Pillow skips visual QA checks silently with a logged WARNING
rather than crashing the reviewer.

GAP 4 — No fallback for legacy subfolder layouts
Status: FIXED
Evidence:
- Line 2627-2631: "Primary path: resources/images/. Fallback: resources/ directly for legacy builds.
  images_dir_local = _resources_base  # legacy layout — images may sit at resources/ root"
- `_resolve_version_root()` (line ~911): handles the case where a child folder (png/motion/resources)
  is passed instead of the version folder root — resolves it up to the version root.
- Legacy tip template checks (line 321-322) are separate from smart-plan carousels and each path
  has independent handling.

---

## What this means for Phase 1 / Phase 2

The rebuild-phase-decision-2026-07-09.md recommended Phase 1 (fix these 4 gaps) before Phase 2
(Wealth/Power deck). Since all 4 gaps are fixed, the only remaining Phase 1 item is:

From the decision doc's action table:
Action 2 — "Run OPC talking-head dry-run end-to-end and verify Drive path" (still pending)
Action 3 — "Draft Wealth/Power deck HTML template" (pending Phase 2)
Action 4 — "Pick first Brazil Wealth/Power topic from Content Queue" (Priscila's decision)

The pipeline dry-run (Action 2) is blocked by the content automation PAUSE (2026-06-26).
Once Priscila confirms pipeline restart, one dry-run OPC carousel build verifies the path.
After that, Phase 2 can start immediately.

---

## Recommendation

Update the rebuild-phase-decision-2026-07-09.md status from "Phase 1 in progress" to
"Phase 1 complete (carousel reviewer gaps fixed); pipeline dry-run pending restart decision."

No code changes needed in carousel_reviewer.py based on this audit.
The file is production-ready for Phase 2 from the reviewer's perspective.
