# Content Creator V2 — Status

Last updated: 2026-08-05
Current branch: `claude/content-creation-system-audit-4xuawe`
Current package: **Package 0 — Repository Baseline & Collision Audit (COMPLETE)**
Current phase: Audit complete → awaiting Priscila review before Package 1
Last completed action: Wrote `docs/content-creator-v2/CODE_AUDIT.md` from a real repository audit
Next action: Priscila reviews CODE_AUDIT.md; then re-scoped Package 1 (extend existing `content_creator_v2/contracts.py`)

## Current state

Package 0 executed as a **documentation-only** audit. The existing content/media pipeline was read at symbol level across `content_creator/`, `content_creator_v2/`, `capture/`, `research/`, and `remotion/`. Every planned V2 component was assigned a REUSE/EXTEND/ADAPT/RECREATE/REPLACE LATER/NEW decision in `CODE_AUDIT.md`.

Headline result: **the V2 data contracts already exist** as dataclasses in `scripts/content_creator_v2/contracts.py` (MediaAsset, Scene, ShotRequest, ClipCandidate, ApprovedShot, EditDecision). Package 1 is therefore re-scoped from "create contracts" to "reconcile + complete + version + test the existing contracts." The render, transcription, and provider-fallback layers are mature and reusable; the missing "brain" is scene/keyframe extraction, embeddings/semantic search, a shot planner, and a clip contact-sheet approval artifact.

## Current rule

Package 0 real audit comes before coding. **No runtime changes until CODE_AUDIT.md is reviewed by Priscila.** Package 0 does not replace the Security/2FA-bypass gate (Focus row 87); both gates remain.

## Source-of-truth links

- Google Doc (branch canonical): `CONTENT CREATOR V2 — IMPLEMENTATION PACKAGES FOR CODEX & CLAUDE — 2026-08-05` (`1l_hrf-ppXwIMRA5h61dZQ4z_pY_r8XYrLSq9_ZSBKM4`)
- Google Doc (cited inside `content_creator_v2/contracts.py`, **must be reconciled**): `1DjLeV5Ba5jXM4eY-7D0EZSCzzhgCJU8i1u0JDE2lQXU`
- README & Project Index: `1nJf-qLOugKCgfpqMw5DZWE9JgGjcPSJysdYFe1hob5g`
- Project Tracker (Sheet): `1oXdYr0Kv0huVPJufphdWSVEWo0jzf44Ay-y87ZGmWWQ`
- `docs/content-creator-v2/SOURCE_OF_TRUTH_AND_STORAGE.md`
- `docs/content-creator-v2/ATHENA_FOCUS_HANDOFF.md`
- `docs/content-creator-v2/PLANNING_CLOSURE_CHECKLIST.md`
- `docs/content-creator-v2/PROJECT_EXECUTION_PLAYBOOK.md`
- `docs/content-creator-v2/EXTERNAL_APPS_AND_REPOS_RESEARCH_PLAN.md`
- `docs/content-creator-v2/MVP_ACCELERATION_REPO_RESEARCH.md`
- Docs source branch: `content-creator-v2/docs-source-of-truth-2026-08-05`
- Focus: `_Focus Partner — STATE`, tab `Pending`, rows ~1104–1117 — **not verified this session** (Focus not reachable from non-interactive run).

## Package progress

| Package | Name | Status | Notes |
| --- | --- | --- | --- |
| 0 | Repository audit | **Complete** | `CODE_AUDIT.md` + `STATUS.md` written; docs-only |
| 1 | Contracts/enums | **Ready (re-scoped)** — pending review | EXTEND `content_creator_v2/contracts.py`; add 5 contracts + enums/errors/tests |
| 2 | SQLite/catalog/cache | Blocked until P1 | NEW; `clips_manifest.py` is JSON-only stopgap |
| 3 | Ingest/ffprobe | Blocked until P2 | ADAPT: extract shared ffprobe wrapper |
| 4 | Scenes/keyframes/transcripts | Blocked until P3 | transcription REUSE; scene/keyframe NEW |
| 5 | Semantic search/ranking | Blocked until P4 | embeddings/search NEW (highest risk); ranking ADAPT |
| 6 | Provider adapters/fallback | Blocked until P5 | ADAPT `route_state.py` + `motion_sources` SOURCE_CHAIN |
| 7 | Script assistant/shot planner | Blocked until P6 | assistant ADAPT; shot planner NEW |
| 8 | Approval artifact/edit decision | Blocked until P7 | contact sheet NEW; `approval_handler` adapt concepts only |
| 9 | Remotion integration | Blocked until P8 | EXTEND `build_render_props.py` + `manifest_renderer` |
| 10 | Quality/security/ops | Blocked until P9 | `SECURITY_AND_STORAGE_GATES.md` + `.gitignore` V2 patterns NEW |

## What changed this session

- Created `docs/content-creator-v2/CODE_AUDIT.md` (real Package 0 findings + decision table).
- Created `docs/content-creator-v2/STATUS.md` (this file).
- Brought the canonical source-of-truth doc set onto the audit branch (checked out from `content-creator-v2/docs-source-of-truth-2026-08-05`) so the audit's sibling references resolve. Documentation only.

## Files changed

| File | Change | Runtime impact |
| --- | --- | --- |
| `docs/content-creator-v2/CODE_AUDIT.md` | Created | None (docs) |
| `docs/content-creator-v2/STATUS.md` | Created | None (docs) |
| `docs/content-creator-v2/*` (source-of-truth set) | Added to this branch from docs branch | None (docs) |

## Commands run

| Command | Purpose |
| --- | --- |
| `git ls-files` / `git ls-tree` | Map repo (508 tracked files) and subsystem trees |
| `grep` capability sweep (ffprobe/ffmpeg/whisper/srt/scene/sqlite/embeddings/checksum/yt-dlp) | Locate existing capabilities |
| `cat scripts/content_creator_v2/contracts.py` | Confirm existing V2 contracts |
| signature extraction over `scripts/research/*`, `capture/*`, `remotion/*` | Map symbols without full reads |
| `git checkout <docs-branch> -- docs/content-creator-v2/` | Bring sibling docs onto audit branch |

## Tests run

| Command | Result | Notes |
| --- | --- | --- |
| (none) | — | Package 0 is documentation-only; no code executed. `scripts/content_creator_v2/` currently has **zero tests** — the first Package 1 artifact is `tests/test_contracts.py`. |

## Things not touched

- `main` branch
- production workflows (`.github/workflows/*`)
- secrets / `.env` / cookies / OAuth tokens
- Drive route IDs / production Sheets
- media originals / caches / embeddings / generated reels
- `approval_handler.py` (Gmail/Buffer publish)
- `motion_sources.py` behavior (NN-M1..M5 locked)
- `main.py` (2,966-line monolith)

## Production-impact statement

**Zero production impact.** No runtime code, workflow, secret, Drive route, Sheet, media file, or email/approval flow was modified. Only Markdown under `docs/content-creator-v2/` was added.

## Secrets / media / storage statement

No secrets read or written. No media committed (`git ls-files` confirms zero `.mp4/.mov/.sqlite/.db/.npy/.jsonl` tracked). **Open risk:** `.gitignore` lacks the SOURCE_OF_TRUTH V2 ignore patterns (`*.clip_finder.sqlite`, `*.embeddings.*`, `**/keyframes/`, `**/thumbnails/`, `**/generated_reels/`, `content_creator_cache/`) — these must be added before any package that generates caches/media.

## Risks

1. Duplicate-contract collision if Package 1 ignores existing `content_creator_v2/contracts.py`.
2. Two live master-plan docs (`1l_hrf-…` vs `1DjLeV5Ba…`) — reconcile before editing contracts.
3. `.gitignore` missing V2 media/cache patterns.
4. Mac M3 8GB memory limit for Package 5 embeddings (highest technical risk).
5. `main.py` blast radius — wrap-only.
6. Focus rows 1104–1117 not verified this session.

## Open decisions

- Contracts location: keep `scripts/content_creator_v2/` (recommended) vs the prompt's `scripts/content_creator/clip_finder/`.
- Contract library: stay on stdlib `dataclasses` (recommended, no new dep) vs Pydantic.
- Which master-plan Google Doc is canonical.

## Stop conditions

- Do not begin Package 1 before Priscila reviews `CODE_AUDIT.md`.
- Do not create a second contracts module — extend the existing one.
- Do not touch any FORBIDDEN file listed in `CODE_AUDIT.md`.
- Do not write real media, secrets, or production Sheets/Drive.
- Do not open a PR unless Priscila explicitly asks.

## Next exact action

Priscila reviews `CODE_AUDIT.md`. On approval, run **re-scoped Package 1**: extend `scripts/content_creator_v2/contracts.py` (+ `enums.py`, `errors.py`, `__init__.py`, `tests/test_contracts.py`) after reconciling the two master-plan docs and confirming the module location.

## Next prompt (Package 1, only after review)

> Implement Content Creator V2 Package 1 (contracts) by **extending** `scripts/content_creator_v2/contracts.py` — do not create a new module. First reconcile master-plan docs `1l_hrf-…` and `1DjLeV5Ba…`. Add `schema_version` and the missing contracts `TranscriptSegment`, `Keyframe`, `ProvenanceRecord`, `ProcessingResult`, `RenderResult`. Add `enums.py`, `errors.py`, `__init__.py`, and `tests/test_contracts.py` covering: JSON round-trip, invalid timestamp ranges, unsupported schema major version, invalid orientation, missing provenance, provider-specific metadata isolation. Stay on stdlib dataclasses. No network, Drive, real media, or production Sheets. Do not touch main.py, motion_sources.py, approval_handler.py, capture_pipeline.py, workflows, or secrets. Update STATUS.md. Do not push to main or open a PR unless Priscila asks.

## Handoff summary

- **Summary:** Package 0 done, docs-only. V2 contracts already exist → Package 1 re-scoped to extend, not create. Render/transcription/fallback layers reusable; scene/keyframe/embeddings/shot-planner/contact-sheet are the real NEW work.
- **Links:** `CODE_AUDIT.md` (this folder); source-of-truth docs (this folder); docs branch `content-creator-v2/docs-source-of-truth-2026-08-05`.
- **Risks:** duplicate contracts, two master-plan docs, `.gitignore` gaps, Mac M3 8GB embeddings.
- **Next package:** Package 1 (contracts) — ready and re-scoped, pending Priscila review.
