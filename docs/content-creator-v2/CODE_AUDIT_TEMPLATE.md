# CODE_AUDIT.md Template — Content Creator V2

Use this template when executing Package 0.

Do not mark Package 0 complete until this template is filled with real repository findings.

## Package 0 rules

- Documentation-only.
- Do not change runtime code.
- Do not push to main.
- Do not open PR before Priscila review.
- Do not modify secrets, workflows, Drive routes, Sheets, media, approval email flows, or production scripts.

## Sources read

| Source | Read? | Notes |
| --- | --- | --- |
| NONNEGOTIABLES.md |  |  |
| AGENTS.md |  |  |
| scripts/content_creator/main.py |  |  |
| scripts/content_creator/motion_sources.py |  |  |
| scripts/content_creator/approval_handler.py |  |  |
| scripts/content_creator/manual_builder/README.md |  |  |
| docs/content-creator-rebuild-phase1-spec.md |  |  |
| scripts/capture/capture_pipeline.py |  |  |
| Remotion-related files |  |  |
| FFmpeg-related files |  |  |
| Whisper/transcription files |  |  |
| SRT/caption files |  |  |
| tests |  |  |
| Focus rows 1104–1114 |  |  |
| SOURCE_OF_TRUTH_AND_STORAGE.md |  |  |
| ATHENA_FOCUS_HANDOFF.md |  |  |
| PLANNING_CLOSURE_CHECKLIST.md |  |  |
| PROJECT_EXECUTION_PLAYBOOK.md |  |  |
| EXTERNAL_APPS_AND_REPOS_RESEARCH_PLAN.md |  |  |

## Existing component map

| Requirement | Existing file/symbol | Decision | Reason | Allowed package | Risk | Test required |
| --- | --- | --- | --- | --- | --- | --- |
| MediaAsset contract |  |  |  | Package 1 |  |  |
| Scene contract |  |  |  | Package 1 |  |  |
| ShotRequest contract |  |  |  | Package 1 |  |  |
| ClipCandidate contract |  |  |  | Package 1 |  |  |
| EditDecision contract |  |  |  | Package 1 |  |  |
| ProvenanceRecord contract |  |  |  | Package 1 |  |  |
| SQLite helper/catalog |  |  |  | Package 2 |  |  |
| Migrations |  |  |  | Package 2 |  |  |
| Checksum/fingerprint |  |  |  | Package 2 |  |  |
| ffprobe wrapper |  |  |  | Package 3 |  |  |
| Local media ingest |  |  |  | Package 3 |  |  |
| Apple Photos/job-site index |  |  |  | Package 3 / Dataset |  |  |
| Scene segmentation |  |  |  | Package 4 |  |  |
| Keyframe extraction |  |  |  | Package 4 |  |  |
| Whisper/transcription adapter |  |  |  | Package 4 |  |  |
| Embeddings |  |  |  | Package 5 |  |  |
| Semantic search |  |  |  | Package 5 |  |  |
| Ranking |  |  |  | Package 5 |  |  |
| Provider interface |  |  |  | Package 6 |  |  |
| motion_sources adapter |  |  |  | Package 6 |  |  |
| Script assistant |  |  |  | Package 7 |  |  |
| Shot planner |  |  |  | Package 7 |  |  |
| Approval contact sheet |  |  |  | Package 8 |  |  |
| Existing Gmail approval flow |  |  |  | Package 8+ |  |  |
| Remotion adapter |  |  |  | Package 9 |  |  |
| Export/provenance manifest |  |  |  | Package 9–10 |  |  |
| Security/storage gate |  |  |  | Package 10 |  |  |

Decision vocabulary:

- REUSE
- EXTEND
- ADAPT
- RECREATE
- REPLACE LATER
- NEW
- FORBIDDEN UNTIL LATER

## Forbidden files until later

List files that must not be edited before the allowed package.

| File/path | Forbidden until | Why |
| --- | --- | --- |
| scripts/content_creator/main.py |  |  |
| scripts/content_creator/motion_sources.py |  |  |
| scripts/content_creator/approval_handler.py |  |  |
| scripts/capture/capture_pipeline.py |  |  |
| GitHub workflows |  |  |
| production Sheets/Drive route files |  |  |
| secrets/env files | Always |  |
| media folders/cache | Always |  |

## External evidence reconciliation

| Candidate | Classification | How it informs V2 | Pilot needed? |
| --- | --- | --- | --- |
| Apple Photos job-site index |  |  |  |
| CapCut |  |  |  |
| Adobe Premiere Media Intelligence |  |  |  |
| Descript |  |  |  |
| Gling |  |  |  |
| FFmpeg |  |  |  |
| Remotion/manual builder |  |  |  |
| ClipsAI |  |  |  |
| MoneyPrinterTurbo |  |  |  |
| deepsearch |  |  |  |
| Remotion prompt-to-video template |  |  |  |

## Package 1 readiness decision

Can Package 1 start?

- Yes / No:
- Required safe files:
- Required tests:
- Blockers:

## No-op / rollback statement

Package 0 changed only documentation. No runtime rollback required.
