# Technical Verification Session — 2026-08-05

Status: focused research session completed enough to freeze architecture direction; Package 0 real repo audit still required.

## What was inspected

### Public / external

- OpenChatCut / agent-native local-first video editing pattern.
- OpenReelio / desktop editor with command log, SQLite project storage, FFmpeg/GPU export.
- Remotion / existing renderer ecosystem.
- Remotion Timeline / UI pattern for timeline control.
- PySceneDetect / scene detection and keyframe extraction.
- CLIP/video-text retrieval research.
- B-Script / transcript-based B-roll recommendation research.
- Script-to-B-roll products: B-Roll Me, ScenePull, Magicroll.

### Internal repository

Initial files inspected or confirmed:

- `scripts/content_creator/main.py`
- `scripts/content_creator/motion_sources.py`
- `scripts/content_creator/approval_handler.py`
- `scripts/content_creator/MOTION_SOURCES_RESEARCH.md`
- `tests/test_motion_sources_clip_collections.py`
- pipeline/routing references found by search

This is not yet the full Package 0 audit. It is an architecture-direction verification.

## Key internal findings

1. `main.py` is a production orchestrator for the current content pipeline and GitHub Actions workflow. It already picks topics, generates carousel content, renders PNG/motion covers, uploads to Drive, emails previews and updates status.

2. `motion_sources.py` is a working fallback source chain for public/curated clips. It includes sidecar attribution and multiple network/source tiers. It should be protected and adapted later, not refactored early.

3. `approval_handler.py` already handles Gmail reply parsing, approval/change requests, Buffer scheduling and content status transitions. V2 approval should not replace this early.

## Architecture freeze

Content Creator V2 should be:

```text
Idea
→ Script
→ Shot Plan
→ Semantic Clip Search
→ Timeline JSON
→ Human Approval
→ Renderer
→ Export / Provenance Log
```

## Highest-value external patterns to adopt

1. **Agent-native editable timeline**
   - AI edits should be tool/action based and inspectable.
   - Do not produce opaque final files without review.

2. **Timeline JSON / project state as source of truth**
   - Renderer, approval artifact and future editor can all consume the same structure.

3. **Command/action log mindset**
   - Every change should be explainable and reversible.

4. **Scene/keyframe/contact sheet before full editor**
   - Static approval artifact is enough for MVP.

5. **Script-to-shot decomposition**
   - B-roll systems prove that script should become visual moments before searching assets.

## Immediate decisions

- Keep Remotion/FFmpeg as first render target through adapter.
- Build V2 beside current production pipeline.
- Use personal OPC footage first.
- Use existing `motion_sources.py` only as fallback adapter in later package.
- Require Timeline JSON before approval/render.
- Do not build a full desktop timeline editor in MVP.
- Do not run a full Apple Photos scan before the approved-folder MVP works.

## What is still not done

- Full `CODE_AUDIT.md` of every relevant repo file.
- Full `STATUS.md` generated from actual code state.
- Dependency inventory from package files.
- Test inventory and current test run.
- Security/storage review of tokens, Drive IDs, cache paths and secret handling.
- Dataset manifest for 10–20 approved test videos.

## Next package

Execute Package 0C: Current Repo Technical Audit.

Package 0C must be read-only with respect to runtime code and should produce:

- `CODE_AUDIT.md`
- `STATUS.md`
- `DEPENDENCY_INVENTORY.md`
- `DATA_FLOW.md`
- `SECURITY_AND_STORAGE_REVIEW.md`

No Package 1 coding until those files exist.
