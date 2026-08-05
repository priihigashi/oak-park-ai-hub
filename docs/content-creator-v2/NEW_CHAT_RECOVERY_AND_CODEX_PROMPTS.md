# Content Creator V2 — New Chat Recovery + Codex Package 0 Prompts

Created: 2026-08-05
Repository: `priihigashi/oak-park-ai-hub`
Branch: `content-creator-v2/docs-source-of-truth-2026-08-05`
Status: documentation only. No runtime code should be changed from this file.

## Purpose

This file exists so Priscila does not have to re-explain the Content Creation System every time a new ChatGPT/Codex/Claude session starts.

The next agent should use this as the shortest durable handoff:

1. Recover the correct Drive/GitHub/Focus context.
2. Confirm the current storage and folder rules.
3. Run the next safe implementation step.
4. Avoid creating another disconnected folder, tracker, branch, or pipeline.

---

## NEW CHAT RECOVERY PROMPT

Paste this into a new chat when continuing this project:

```text
You are continuing Priscila McFolling's Content Creation System / Content Creator V2 project.

Start by recovering the source of truth. Do not rely only on chat memory.

Open / search these anchors:

1. Google Drive: Marketing Shared Drive / Claude Code Workspace.
2. Current visual project staging folder: _Active Projects / Content Creation System.
   Important: _Active Projects was created on 2026-08-05 and is provisional until a Drive Structure Audit confirms whether it should remain canonical, move, or become shortcut-only.
3. Google Doc: CONTENT CREATOR V2 — IMPLEMENTATION PACKAGES FOR CODEX & CLAUDE — 2026-08-05.
4. Google Doc: Content Creation System — README & Project Index.
5. Google Sheet: Content Creation System — Project Tracker.
6. Focus Sheet: _Focus Partner — STATE, tab Pending. Current relevant rows are around 1104–1117, plus older rows cited in the master plan.
7. GitHub repo: priihigashi/oak-park-ai-hub.
8. GitHub branch: content-creator-v2/docs-source-of-truth-2026-08-05.
9. GitHub docs folder: docs/content-creator-v2/.

Mandatory operating rules:

- Do not create new folders or move files until Drive Structure Audit is complete.
- Do not start runtime coding before Package 0 real audit creates CODE_AUDIT.md and STATUS.md.
- Do not push to main.
- Do not open a PR unless Priscila explicitly asks.
- Do not touch secrets, workflows, production Drive routing, media originals, generated caches, cookies, OAuth tokens, or real personal-media databases.
- Treat existing systems as parts to audit, not as a working product to preserve blindly.
- Every major decision must be saved in Google Doc + GitHub Markdown + Focus pointer or tracker.

Current next work order:

A. Drive Structure Audit / Correction.
B. Public repo / app acceleration research.
C. Package 0 real repository audit.
D. Package 1 contracts only.

If the user says "continue" or "go," continue from the highest unfinished item above, not from a new plan.
```

---

## CODEX PACKAGE 0 PROMPT

Use this exact prompt for Codex or Claude Code when ready to audit the repo:

```text
You are executing Content Creator V2 Package 0 for Priscila McFolling in repository priihigashi/oak-park-ai-hub.

Goal:
Create a real repository audit before any runtime implementation. The output is documentation only.

Branch:
Work on a local branch named content-creator-v2/p00-code-audit unless another branch is explicitly provided by Priscila.

Do not:
- Do not modify runtime code.
- Do not push to main.
- Do not open a PR.
- Do not deploy.
- Do not alter GitHub Actions/workflows.
- Do not change secrets, .env files, credentials, cookies, OAuth tokens, Drive folder IDs, production Sheets, production data, or real media.
- Do not commit Apple Photos exports, job videos, thumbnails, embeddings, SQLite media catalogs, GPS cache, generated reels, or personal media metadata.

Read first:
- NONNEGOTIABLES.md
- AGENTS.md
- docs/content-creator-v2/SOURCE_OF_TRUTH_AND_STORAGE.md
- docs/content-creator-v2/ATHENA_FOCUS_HANDOFF.md
- docs/content-creator-v2/PROJECT_DRIVE_STRUCTURE_STANDARD.md
- docs/content-creator-v2/DRIVE_STRUCTURE_AUDIT_AND_CORRECTION.md if present
- docs/content-creator-v2/MVP_ACCELERATION_REPO_RESEARCH.md if present
- scripts/content_creator/main.py
- scripts/content_creator/motion_sources.py
- scripts/content_creator/approval_handler.py
- scripts/content_creator/manual_builder/README.md
- docs/content-creator-rebuild-phase1-spec.md
- scripts/capture/capture_pipeline.py
- scripts/capture/resource_router.py
- scripts/remotion/export_slides.js

Search for existing code related to:
- MediaAsset / Scene / ShotRequest / ClipCandidate / ApprovedShot / EditDecision / ProvenanceRecord / RenderResult or equivalent older names
- ffprobe / ffmpeg wrappers
- Whisper / transcription / SRT parsing
- Remotion rendering
- Drive upload / folder routing / status updates
- Gmail approval / approval_handler
- image/video thumbnails
- scene detection
- checksums / caching / SQLite
- embeddings / CLIP / vector search
- content routing / content classification
- manual builder / carousel / reel generation
- motion_sources.py fallback chain
- provenance sidecars
- tests for the above

Create or update only these documentation files:

1. docs/content-creator-v2/CODE_AUDIT.md
2. docs/content-creator-v2/STATUS.md

CODE_AUDIT.md must include this table:

Requirement | Existing file/symbol | Decision | Reason | Allowed package | Risk | Tests required | Notes

Decision vocabulary:
- REUSE: existing implementation works and can be called directly.
- EXTEND: existing implementation works but needs bounded expansion.
- ADAPT: wrap existing implementation behind a new interface.
- RECREATE: old approach is too unreliable/messy and should be rebuilt cleanly.
- REPLACE LATER: keep legacy behavior for now but schedule cleanup.
- NEW: no usable implementation exists after audit.

CODE_AUDIT.md must explicitly answer:

1. Which existing files are safe to reuse?
2. Which existing files must not be edited until later packages?
3. Which pieces are duplicated or risky?
4. Which pieces of the old flow failed or are unreliable?
5. Which Package 1 files are safe to create?
6. Which public repo/app patterns might shorten the MVP?
7. What is the shortest safe vertical slice?
8. What should be tested before Package 1 starts?

STATUS.md must include:

- Current branch
- Date/time
- What was read
- What was created or changed
- Tests run, if any
- Commands run
- Production-impact statement
- Secrets/media/storage statement
- Risks
- Next recommended package
- Stop conditions for the next agent

Acceptance criteria:

- No runtime code changed.
- CODE_AUDIT.md exists and covers every Package 1–10 planned component.
- STATUS.md exists and gives a clear next action.
- Existing media/storage/secrets boundaries are preserved.
- Audit states whether Package 1 can begin.

Handoff back to Priscila:

Return a concise summary with:
- files created/changed
- decisions counts by REUSE/EXTEND/ADAPT/RECREATE/REPLACE LATER/NEW
- highest risks
- shortest MVP path
- exact next prompt for Package 1, only if Package 1 is safe
```

---

## PACKAGE 1 START PROMPT AFTER PACKAGE 0 PASSES

Do not use this until CODE_AUDIT.md says Package 1 is safe.

```text
Implement Content Creator V2 Package 1 only: contracts and enums.

Read CODE_AUDIT.md and STATUS.md first.

Create only the safe files confirmed by Package 0, expected under scripts/content_creator/clip_finder/ unless the audit says otherwise:

- __init__.py
- enums.py
- contracts.py
- errors.py
- tests/clip_finder/test_contracts.py

Define versioned typed contracts for:
MediaAsset, Scene, TranscriptSegment, Keyframe, ShotRequest, ClipCandidate, ApprovedShot, EditDecision, ProvenanceRecord, ProcessingResult, RenderResult.

Rules:
- No network calls.
- No Drive calls.
- No real media.
- No production Sheets.
- No changes to main.py, motion_sources.py, approval_handler.py, capture_pipeline.py, resource_router.py, GitHub Actions, secrets, or routing IDs.
- Use Pydantic only if already available or if dependency addition is explicitly documented and low-risk.

Tests:
- JSON round-trip.
- invalid timestamp ranges.
- unsupported schema major version.
- invalid orientation.
- missing provenance.
- provider-specific metadata isolation.

Update STATUS.md with exact files, commands, test results and next package.
Do not push to main or open a PR unless Priscila explicitly asks.
```

---

## Copy/paste summary for human context

This project is about making Priscila's construction/social content system actually useful: find clips from her own footage, map them to scripts, show candidates for approval, then render drafts without losing originals or creating another broken pipeline.

The next work is not new architecture. It is controlled audit + smallest working slice.
