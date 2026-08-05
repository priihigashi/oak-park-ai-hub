# Content Creator V2 — Architecture Decisions

Created: 2026-08-05
Status: frozen for Package 0 / Package 1 planning. May change only through a dated architecture decision update.

## Decision 1 — Timeline JSON is the core contract

Content Creator V2 will not pass raw ad-hoc objects directly from search into rendering. It will produce an explicit timeline/edit decision document.

Canonical flow:

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

Reason:
- Public AI editor patterns converge on editable project state, command/action logs and reversible timeline changes.
- Existing repo already has Remotion/FFmpeg render assets, so V2 should adapt into them through a data contract.
- JSON can be inspected by Priscila, Codex, Claude, Jarvis/Athena and tests.

## Decision 2 — Personal footage first

Source priority is frozen:

```text
1. Personal / OPC media library
2. Approved curated clip collections
3. Public fallback sources
```

Existing `scripts/content_creator/motion_sources.py` remains valuable, but only as a fallback adapter in later packages. It must not become the V2 search/indexing layer.

## Decision 3 — MVP is local-first and lightweight

The MVP targets MacBook Air M3 / 8 GB constraints.

Preferred first implementation:
- local catalog
- ffprobe metadata
- scene/keyframe extraction
- transcript extraction only when useful
- lightweight embeddings
- SQLite-based manifest/cache
- static contact sheet / approval artifact
- Remotion/FFmpeg render adapter

Avoid for MVP:
- full desktop NLE
- heavy vector DB service
- GPU-heavy trained video model
- automatic Apple Photos full-library scan before a small approved-folder slice works
- public-stock-first pipeline

## Decision 4 — Approval is a first-class gate

The system must produce an approval artifact before render/export. For MVP this can be HTML/contact sheet + Timeline JSON, not a full editor.

Approval artifact should show:
- script segment / shot request
- candidate clips/scenes
- score/reason
- selected clip
- start/end time
- orientation/quality notes
- source/provenance
- replace/reject option

## Decision 5 — Existing production pipeline is protected

Do not modify production orchestration until V2 has isolated tests and adapters.

Known current repo roles:
- `scripts/content_creator/main.py` is production orchestrator and GitHub Actions pipeline entrypoint.
- `scripts/content_creator/motion_sources.py` is a public/curated clip fallback chain with sidecar attribution.
- `scripts/content_creator/approval_handler.py` polls Gmail replies and handles approval/change-request logic.

V2 modules should be added beside these files, not inside them at first.

## Decision 6 — Backup/archive protection is global

No code, agent, prompt, or workflow may save new live artifacts into folders classified as BACKUP or ARCHIVE.

Jarvis/Athena creation gate must check folder role before saving:

```text
ACTIVE / REFERENCE / ARCHIVE / BACKUP / SYSTEM
```

If destination is BACKUP or ARCHIVE, stop and find the active destination unless the user explicitly requested an archive action.

## Decision 7 — Package order remains gated

Do not begin Package 1 until Package 0 creates real audit outputs.

Package 0 must produce:
- `CODE_AUDIT.md`
- `STATUS.md`
- `DEPENDENCY_INVENTORY.md`
- `DATA_FLOW.md`
- `SECURITY_AND_STORAGE_REVIEW.md`
- updates to implementation package sequencing

## Frozen MVP vertical slice

```text
approved OPC folder
10–20 videos
metadata + scene/keyframes
local catalog
shot planner from one script
semantic/keyword ranking
contact sheet approval
Timeline JSON
Remotion/FFmpeg draft render
provenance log
```

## Decision summary table

| Area | Frozen decision |
|---|---|
| Core contract | Timeline JSON / Edit Decision JSON |
| Main media source | Personal OPC media first |
| First renderer | Existing Remotion/FFmpeg path via adapter |
| First UI | Static approval/contact sheet |
| Scene detection | PySceneDetect or FFmpeg first |
| Search | Hybrid visual semantic + transcript/keyword + ranking |
| Storage | Local catalog/cache; no private media in GitHub |
| Existing production files | Read/reuse/adapt later; do not refactor in early packages |
| Backup folders | Read-only recovery only |
