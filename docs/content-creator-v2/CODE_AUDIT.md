# Content Creator V2 — Code Audit

Date: 2026-08-05
Branch: `docs/content-creator-v2-audit-2026-08-05`
Scope: documentation-only audit; no runtime code changed.

## Executive conclusion

The current implementation has useful production pieces, but it is not yet the Content Creator V2 architecture.

Current system is mostly:

`capture / source URL -> transcript / metadata -> classifier or direct content generation -> carousel/post build -> Drive upload -> preview email -> approval handler`

Target V2 should become:

`Idea -> Script -> Shot Plan -> Semantic Clip Search -> Timeline JSON -> Human Approval -> Renderer -> Export / Provenance Log`

The highest-value change is not more rendering code. It is a strict contract layer: **Timeline JSON becomes the module boundary** between planning, search, approval, rendering, and provenance.

## Creation Gate / workspace safety audit

### Current state

Existing locked rules already cover several storage policies:

- Shared Drive is default, not My Drive.
- `supportsAllDrives=True` is required for Drive API calls.
- News must not be stored in Marketing Drive.
- Every new flow doc must be logged in Flow Plans Tracker.
- Every new spreadsheet/tab must be logged in the spreadsheet hub.
- Script edits require full-file read and surgical changes.

### Gap

There is no explicit pre-create rule that forces every file/folder/doc save through:

1. Flow Plans Tracker — Master Index
2. Drive Map — ALL DRIVES
3. Drive Map — Marketing
4. Drive Map — OPC where relevant
5. Focus rows
6. GitHub docs
7. Google Drive exact/similar-name search
8. folder role classification before saving

There is also no explicit folder-role enum in the audited files: `ACTIVE`, `REFERENCE`, `ARCHIVE`, `BACKUP`, `SYSTEM`.

### Required standard before runtime changes

Add a Jarvis/Athena standard called `Creation Gate` before any new save/create/move operation.

The rule must answer:

- Is this an existing product, flow, doc, tracker, asset, or task?
- Is there already a canonical row?
- Is there already a canonical physical location?
- Is the target location `ACTIVE`, `REFERENCE`, `ARCHIVE`, `BACKUP`, or `SYSTEM`?
- Should this update/link an existing item instead of creating a new item?

### Refusal rule

Jarvis/Athena must refuse to save into `BACKUP` or `ARCHIVE` unless the user explicitly says the action is archival/recovery.

Mac reset, migration, export, and backup-created folders are `BACKUP` unless explicitly reclassified.

If a live file is found in a backup folder, flag it as `RESCUE_REQUIRED`; do not continue using that folder as a live home.

## Audited repository files

### `NONNEGOTIABLES.md`

Status: `REUSE + EXTEND`

Reuse:

- Central locked-rule file already exists.
- It already contains Drive/shared-drive rules, logging rules, content routing rules, and code-editing rules.
- It is the correct home for public-safe Jarvis/Athena standards that affect this public repo.

Extend:

- Add Creation Gate.
- Add folder role enum.
- Add backup/archive refusal.
- Add duplicate-detection requirement.
- Add canonical metadata required for saved items.

Do not add private account details or private workspace content to public repo.

### `AGENTS.md`

Status: `REUSE + DO NOT EXPAND WITH PRIVATE DATA`

The public `AGENTS.md` is intentionally stripped of private agent rules and points to a private canonical source. That is correct for a public repo.

Use it only for public-safe behavior rules. Do not reintroduce personal account details, credentials, private inbox details, finance notes, family details, or private memory.

### `scripts/content_creator/main.py`

Status: `REUSE + EXTEND LATER`

Reuse:

- Existing orchestrator structure.
- Work directory pattern.
- alert digest pattern.
- environment-gated features.
- reviewer gate before email.
- routing through `routing.py`.

Gaps for V2:

- The current pipeline does not have explicit `Idea -> Script -> Shot Plan -> Semantic Clip Search -> Timeline JSON` modules.
- Build output is still carousel/post-oriented, not timeline-contract-oriented.
- Timeline JSON is not yet the central handoff object.

Do not refactor this first. Create contracts and tests first.

### `scripts/content_creator/motion_sources.py`

Status: `REUSE + ADAPT`

Reuse:

- Ordered source cascade.
- Non-fatal tier failures.
- sidecar attribution file writing.
- byte-size/duration guards.
- Clip Collections and external URL fallback concepts.

Adapt:

- Convert source lookup into a semantic search result provider that returns clip candidates, not final rendered motion decisions.
- Preserve provenance per candidate.
- Split `source discovery` from `timeline placement`.

Do not add stock-provider sprawl. Current architecture already retired the old 8-tier cascade.

### `scripts/content_creator/approval_handler.py`

Status: `REUSE + EXTEND`

Reuse:

- Human approval loop through email replies.
- LLM fallback cascade for parsing feedback.
- per-slide feedback extraction.

Extend:

- Approval should review Timeline JSON before render/export.
- Feedback should patch the plan/timeline contract, not only post-build variants.
- Add statuses: `timeline_pending_approval`, `approved_to_render`, `revision_requested`, `export_approved`.

### `scripts/content_creator/manual_builder/README.md`

Status: `REUSE`

Reuse:

- Deterministic rendering guidance.
- Google Drive for Desktop save route.
- exact OPC brand tokens.
- clear distinction between carousel and reel sizes.
- EXIF-strip requirement for personal/project photos.

Add:

- Creation Gate must run before choosing the save folder.
- Backup/archive mounted folders are read-only recovery sources.

### `docs/content-creator-rebuild-phase1-spec.md`

Status: `EXTEND + PARTIALLY SUPERSEDE`

Still useful:

- Transcript verification.
- Classifier output schema.
- low-confidence `unrouted` behavior.
- tests for classifier routing.

Needs V2 update:

- Phase 1 should now include Creation Gate standards and timeline-contract planning.
- Classifier should feed `Idea` and `Script` stages, not template filling directly.
- `unrouted` should include duplicate-review and canonical-home checks where storage is involved.

### `scripts/capture/capture_pipeline.py`

Status: `REUSE + EXTEND`

Reuse:

- multi-source capture metadata.
- yt-dlp audio extraction.
- Whisper transcript generation.
- Apify metadata enrichment.
- routing.py source of truth.
- quota/error handling pattern.

Extend:

- capture outputs should become `Idea` records with provenance, not direct post assumptions.
- capture should create/read canonical owner/product, canonical folder, Focus row, and GitHub doc relation before saving final artifacts.
- never save capture outputs into backup/reset locations.

## Current implementation classification by feature

| Feature | Classification | Reason |
|---|---:|---|
| Locked rules registry | REUSE + EXTEND | Existing `NONNEGOTIABLES.md` is correct central surface, but missing Creation Gate. |
| Public/private rule split | REUSE | `AGENTS.md` correctly keeps private rules out of public repo. |
| Capture pipeline | REUSE + EXTEND | Good metadata/transcript base; must output canonical Idea records. |
| Whisper transcription | REUSE | Already part of capture flow; add quality verification before planning. |
| Classifier phase spec | EXTEND | Low-confidence routing is right; redirect output into V2 staged pipeline. |
| Motion source cascade | ADAPT | Keep source/provenance logic, but turn into candidate search provider. |
| Approval handler | EXTEND | Keep human loop; approve Timeline JSON before rendering. |
| Manual OPC builder docs | REUSE | Good deterministic render guidance and brand constraints. |
| Ken Burns legacy | DO NOT TOUCH YET | Retired; do not reintroduce. |
| Remotion renderer | DO NOT TOUCH YET | Frozen until contract is defined and tests pass. |
| Runtime orchestrator refactor | DO NOT TOUCH YET | Too risky before contracts/tests/docs are updated. |
| Semantic clip search | BUILD NEW | Not present as a local-first module. |
| Timeline JSON contract | BUILD NEW | Central missing abstraction. |
| Provenance log | BUILD NEW | Sidecars exist for clips; full export provenance log is missing. |
| Folder role awareness | BUILD NEW | Missing explicit role enum and refusal logic. |
| Duplicate review routing | BUILD NEW | Missing explicit tab/workflow behavior. |

## Audit decision

Do not start Package 1.

Package 0 must formalize safety and contracts first:

1. Creation Gate standard.
2. folder-role enum.
3. duplicate detection protocol.
4. canonical saved-item metadata schema.
5. Timeline JSON schema.
6. provenance schema.
7. test fixtures for classification and contract validation.
