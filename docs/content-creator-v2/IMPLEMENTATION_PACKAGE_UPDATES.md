# Content Creator V2 — Implementation Package Updates

Created: 2026-08-05
Status: apply before Package 0 execution and Package 1 coding.

## Why this file exists

Public repo/commercial workflow research changed the implementation emphasis. The plan should now be timeline-data-first instead of renderer-first.

## Updated package order

### Package 0A — Workspace / Creation Gate Safety

Purpose:
- Prevent repeat of the backup-folder problem.
- Ensure Jarvis/Athena/Codex/Claude never save live files to reset/backup/archive folders.

Required outputs:
- Folder-role registry standard: ACTIVE, REFERENCE, ARCHIVE, BACKUP, SYSTEM.
- Creation Gate prompt/policy in docs.
- Duplicate Review workflow in Flow Plans Tracker.
- Backup folders treated as read-only.

### Package 0B — Public Repo / Tool Acceleration Audit

Purpose:
- Compare current architecture to public tools/repos.
- Decide what patterns to adopt.

Required outputs:
- `PUBLIC_REPO_COMPARISON.md`
- `ARCHITECTURE_DECISIONS.md`
- list of patterns adopted/rejected

### Package 0C — Current Repo Technical Audit

Purpose:
- Inspect current repo and classify everything as REUSE / EXTEND / ADAPT / RECREATE / REPLACE LATER / BUILD NEW / DO NOT TOUCH YET.

Required outputs:
- `CODE_AUDIT.md`
- `STATUS.md`
- `DEPENDENCY_INVENTORY.md`
- `DATA_FLOW.md`
- `SECURITY_AND_STORAGE_REVIEW.md`

### Package 1 — Contracts

Update:
- Package 1 must now include first-class timeline/edit-decision contracts.

Required models should include:
- `MediaAsset`
- `SceneSegment`
- `TranscriptSegment`
- `ShotRequest`
- `ClipCandidate`
- `TimelineDecision` or `EditDecision`
- `TimelineTrack`
- `TimelineItem`
- `ApprovalDecision`
- `ProvenanceRecord`

Acceptance:
- Timeline JSON can represent one short Reel with video, captions, audio and text overlays.
- Timeline JSON has stable IDs and source/provenance fields.
- No renderer-specific logic inside the contract models.

### Package 2 — Local Catalog / Storage

Update:
- Store timeline decisions and approval states, not only assets/scenes.
- Use local SQLite-style storage first.
- Plan for vector/FTS hybrid search.

### Package 3 — Ingestion / Metadata

Update:
- Start with an approved OPC folder, not the full Apple Photos library.
- Use ffprobe metadata and filesystem fingerprints.
- Treat Apple Photos full scan as later expansion.

### Package 4 — Scene / Keyframe / Transcript Extraction

Update:
- Prefer PySceneDetect or FFmpeg CLI for first scene split.
- Generate keyframes/contact sheet images for approval.
- Transcript extraction is useful, but visual construction b-roll must not depend only on transcript.

### Package 5 — Search / Ranking

Update:
- Search must be hybrid:
  - semantic visual score
  - transcript/keyword score
  - personal-source bonus
  - orientation/quality score
  - recency/project match
  - duplication/reuse penalty

### Package 6 — Providers / Legacy Fallback

Update:
- Keep existing `motion_sources.py` as a fallback adapter.
- Do not refactor the current fallback chain before V2 is isolated and tested.

### Package 7 — Script / Shot Planner

Update:
- Shot planner should output shot requests aligned to script segments.
- It should include B-roll density and duration hints.

### Package 8 — Approval Artifact

Update:
- Approval artifact reviews the proposed timeline, not just selected clips.
- Must show source/provenance and replacement options.

### Package 9 — Renderer Adapter

Update:
- Remotion/FFmpeg consumes Timeline JSON.
- Renderer should be swappable later.
- No media search logic inside renderer.

## New package gate

No Package 1 coding until:

```text
Package 0A safety documented
Package 0B repo/tool comparison complete
Package 0C repo audit complete
Architecture decisions frozen
Priscila can see what is reused/adapted/new/postponed
```

## Files that early packages should not alter

- `scripts/content_creator/main.py`
- `scripts/content_creator/approval_handler.py`
- `.github/workflows/*`
- production routing files
- secrets/env handling
- existing Drive folder IDs
- existing `motion_sources.py` behavior

These can be read and documented in Package 0. They can be wrapped/adapted only after explicit package approval.
