# Content Creator V2 — Code Audit
**Date:** 2026-11-09  
**Scope:** `scripts/content_creator/` — full module inventory  
**Purpose:** Pre-Sprint 2 baseline. Establishes current status of every module before Phase 2 (story-arc planner) work begins.

---

## Module Inventory

### Core Orchestration

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `main.py` | 2966 | ✅ BUILT | Pipeline orchestrator. Runs 2:30 AM ET via GitHub Actions. Flow: pick topics → generate → render PNGs → upload Drive → email preview → catalog update. |
| `classifier.py` | 261 | ✅ BUILT | Phase 1 Task 2. Niche + format classifier. Confidence gate at 0.75 (< 0.75 → manual-review). DRAFT formats always → manual-review. Rule-based fallback when no API key. |
| `topic_picker.py` | 441 | ✅ BUILT | Picks 3 topics per run (2 OPC + 1 Brazil) from Inspiration Library. |
| `prompt_builder.py` | 375 | ✅ BUILT | Builds Claude prompts per format/niche. |

### Carousel Build & Render

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `carousel_builder.py` | 8255 | ✅ BUILT | Largest file. Renders 10 PNGs per topic (2 variants × 5 slides — OPC). Brazil/USA: unchanged + 3 motion covers. HTML → PNG via Playwright. |
| `opc_template_chooser.py` | 1085 | ✅ BUILT | Selects OPC template by content type. References opc_template_catalog.json. |
| `opc_template_catalog.json` | — | ✅ BUILT | Template registry for OPC format variants. |
| `opc_template_bundles.json` | — | ✅ BUILT | CSS/component bundles per OPC template. |
| `export_variants.js` | 117 | ✅ BUILT | JS export of carousel variants (Playwright side). |
| `export_proof.js` | 78 | ✅ BUILT | JS export for proof/approval images. |
| `build_carousel_reel.sh` | 127 | ✅ BUILT | Shell wrapper for carousel → reel build chain. |

### Review & Validation Gates

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `carousel_reviewer.py` | 3009 | ✅ BUILT | Full carousel review. Calls auto_fixer.py on failures. |
| `visual_reviewer.py` | 337 | ✅ BUILT | Visual quality gate (layout, contrast, face crop). |
| `text_reviewer.py` | 489 | ✅ BUILT | Text fact-check via Claude. Applies edits to cover.html. |
| `vision_validator.py` | 207 | ✅ BUILT | Vision-based validator (runs Claude Vision on rendered PNGs). |
| `news_source_dual_gate.py` | 254 | ✅ BUILT | Requires 2+ outlets for news confidence gate. |
| `motion_static_sibling_gate.py` | 219 | ✅ BUILT | Ensures motion cover has a static sibling. |
| `named_person_face_gate.py` | 193 | ✅ BUILT | Prevents named-person face errors in carousels. |
| `visual_cadence_gate.py` | 214 | ✅ BUILT | Cadence gate: checks visual consistency vs last 5 posts. |
| `opc_source_policy.py` | 186 | ✅ BUILT | OPC-specific source policy enforcement. |
| `claim_ledger.py` | 116 | ✅ BUILT | Tracks claims made in content to prevent repetition. |

### Auto-Repair

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `auto_fixer.py` | 235 | ✅ BUILT | Proactive repair: image mismatch (1A), text fact-check (1B), visual issues (1C). No human in loop. |

### Image Pipeline

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `image_library.py` | 222 | ✅ BUILT | Drive image library access layer. |
| `image_providers.py` | 746 | ✅ BUILT | Multi-provider image sourcing (OpenAI, Ideogram, Recraft, Seedream, Canva cascade). |
| `photo_matcher.py` | 761 | ✅ BUILT | Matches existing Drive photos to content slots. |
| `photo_enhance_core.py` | 234 | ✅ BUILT | Photo enhancement core (OpenAI + Replicate Clarity Upscaler + Gemini). |
| `fix_existing_images.py` | 684 | ✅ BUILT | One-off tool to retroactively fix images in Drive. |

### Motion Pipeline

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `motion_sources.py` | 1182 | ✅ BUILT | 3-renderer (Remotion/Playwright/Ken Burns) + 8-source cascade. |
| `record_motion.js` | 105 | ✅ BUILT | JS motion recording layer. |

### Delivery & Approval

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `email_preview.py` | 332 | ✅ BUILT | Sends email preview to Priscila with rendered PNGs. |
| `send_preview_emails.py` | 136 | ✅ BUILT | Email delivery helper (wraps email_preview). |
| `approval_handler.py` | 1995 | ✅ BUILT | Processes email reply approvals/changes. Routes to auto_fixer or catalog update. |
| `opc_proof_post.py` | 1458 | ✅ BUILT | Handles OPC proof-post workflow (pre-approval posting to private account). |

### Note & Content Parsing

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `note_parser.py` | 776 | ✅ BUILT | Parses capture notes, transcripts, and inbox items for pipeline input. |
| `contract_loader.py` | 39 | ✅ BUILT | Minimal contract/template loader. |

### Phase 2 Modules (Story-Arc Planner)

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `story_outline.py` | 221 | ⚠️ STUB — FLAGGED OFF | Feature-flagged OFF (`STORY_PIPELINE_V2_ENABLED=0`). No LLM calls. Derives outline from already-generated content fields only. Spine tokens: OPC (`hook/cost/teach/apply/sources`), News-5, News-6. Intentionally does not import carousel_builder.py. Ready to wire in — needs integration hook + flag flip. |

### CSS / Static Assets

| File | Status | Notes |
|------|--------|-------|
| `news_history_base.css` | ✅ BUILT | Base CSS for news history format carousels. |
| `opc_standalones.css` | ✅ BUILT | OPC standalone content CSS. |
| `opc_tip_base.css` | ✅ BUILT | OPC tips format base CSS. |
| `fonts/` (dir) | ✅ BUILT | Font assets for carousel rendering. |

### Reference Docs

| File | Status | Notes |
|------|--------|-------|
| `IMAGE_QUALITY_RULES.md` | ✅ Reference | Image quality standards and rules. |
| `MOTION_SOURCES_RESEARCH.md` | ✅ Reference | Research doc for motion source cascade. |

### Manual Builder (subdirectory)

| File | Status | Notes |
|------|--------|-------|
| `manual_builder/build_carousel_slides.py` | ✅ BUILT | Manual/one-off carousel slide builder. |
| `manual_builder/build_cover.py` | ✅ BUILT | Manual cover builder. |
| `manual_builder/build_reel.py` | ✅ BUILT | Manual reel builder. |
| `manual_builder/wealth_power_reel_v1.md` | Reference | Reel brief/spec. |
| `manual_builder/README.md` | Reference | Manual builder docs. |

### Reel Scripts (subdirectory)

Directory `reel_scripts/` — OPC and News reel templates. Not enumerated above; treated as template assets, not core pipeline logic.

---

## Summary

- **Total Python files:** 30 (27,628 lines total)
- **Total JS files:** 3 (300 lines)
- **Shell files:** 1 (127 lines)
- **Status:** Phase 1 is fully built and running. All core pipeline stages (pick → classify → build → review → auto-fix → deliver → approve) are implemented.

---

## Phase 2 Blockers & Requirements

Phase 2 = story-arc planner integration. Key open items before Sprint 2 can start:

1. **PR #314 must be un-drafted.** Sprint 1 CLI surface (schema + extract_metadata + sync) is the foundation Sprint 2 builds on. Status: Draft — Priscila must un-draft.

2. **`story_outline.py` integration.** Module is built and feature-flagged OFF. Sprint 2 work = (a) write integration hook in `main.py`, (b) test with `STORY_PIPELINE_V2_ENABLED=1`, (c) flip flag on. No new module needed — the stub is clean and dependency-free by design.

3. **`STORY_PIPELINE_V2_ENABLED` flag.** Currently `0` in GitHub Actions secrets or env. Must be set to `1` when Sprint 2 is ready to activate.

4. **Outdated older PRs.** PRs #274 (capture dispatch fix) and #271 (scheduler fix) are 71–77 days old and non-draft. These patches may conflict with Sprint 2 changes if left unmerged. Recommend merging before Sprint 2 begins.

5. **Dependabot PRs (#279–#288).** 10 open dependency bumps (actions/checkout, actions/setup-python, etc.). Low risk — merge in batch before Sprint 2 to avoid stale CI environments.

---

## Next Step

This audit is Package 0 for Sprint 2, as specified in the pipeline-restart-decision-2026-08-02.md. With this doc in place, Sprint 2 can begin with accurate assumptions.

Sprint 2 entry point: wire `story_outline.py` into `main.py` (one integration hook, `STORY_PIPELINE_V2_ENABLED=1` guard) and test end-to-end with one OPC topic.
