# Content Creator V2 — Status

Date: 2026-08-05
Branch: `docs/content-creator-v2-audit-2026-08-05`
Runtime code changed: no.
PR opened: no.
Pushed to main: no.

## Current status

Planning is not frozen yet.

The current repo has a working/partial content pipeline foundation, but Content Creator V2 still needs a documentation and contract package before runtime implementation begins.

## Gates before Package 1

| Gate | Status | Notes |
|---|---:|---|
| Public repo/tool research documented | DONE IN THIS BRANCH | See `PUBLIC_REPO_COMPARISON.md`. |
| Current repo audit documented | DONE IN THIS BRANCH | See `CODE_AUDIT.md`. |
| Backup/archive safety rules documented | DONE IN THIS BRANCH | See `SECURITY_AND_STORAGE_REVIEW.md` and `ARCHITECTURE_DECISIONS.md`. |
| Implementation packages updated | DONE IN THIS BRANCH | See `IMPLEMENTATION_PACKAGE_UPDATES.md`. |
| Timeline JSON named as module contract | DONE IN THIS BRANCH | See `DATA_FLOW.md` and `ARCHITECTURE_DECISIONS.md`. |
| Runtime implementation started | NOT STARTED | Intentionally blocked until Priscila reviews. |
| Tests added | NOT STARTED | Next package should add schema tests before runtime changes. |
| Drive files moved | NOT DONE | Explicitly prohibited. |
| Archive/delete actions | NOT DONE | Explicitly prohibited. |

## What exists and can be reused

| Existing component | Decision | Use in V2 |
|---|---:|---|
| `NONNEGOTIABLES.md` | REUSE + EXTEND | Add public-safe Creation Gate and folder-role policy. |
| `AGENTS.md` | REUSE | Keep private/public split. Do not add private workspace details. |
| `scripts/capture/capture_pipeline.py` | REUSE + EXTEND | Capture becomes Idea/provenance input, not direct template filling. |
| `docs/content-creator-rebuild-phase1-spec.md` | EXTEND | Keep transcript verification and classifier gates; add staged V2 flow. |
| `scripts/content_creator/motion_sources.py` | ADAPT | Convert source cascade into semantic clip-candidate provider. |
| `scripts/content_creator/approval_handler.py` | EXTEND | Approve Timeline JSON before render/export. |
| `scripts/content_creator/manual_builder/README.md` | REUSE | Keep deterministic render and Drive-for-Desktop guidance. |
| current rendering/export helpers | DO NOT TOUCH YET | Wait for schema and validation. |
| Remotion legacy paths | DO NOT TOUCH YET | Frozen until Phase 2/renderer work. |

## Current blocker

The missing layer is not a renderer. The missing layer is the contract:

`timeline.json` must describe tracks, clips, timings, captions, overlays, source provenance, approvals, and export settings before any renderer runs.

Without that, changes will keep creating one-off pipeline branches and workspace mess.

## Required next package

Execute **Package 0 — Safety + Contracts Freeze**.

Package 0 should update standards and add schema/test-only files, still avoiding runtime behavior changes until the contract is reviewed.

## Package 0 checklist

1. Add Creation Gate to `NONNEGOTIABLES.md` or a public-safe linked standards doc.
2. Add folder-role enum: `ACTIVE`, `REFERENCE`, `ARCHIVE`, `BACKUP`, `SYSTEM`.
3. Add refusal policy for `BACKUP`/`ARCHIVE` write targets.
4. Add duplicate-detection protocol and Duplicate Review routing.
5. Add canonical saved-item metadata schema.
6. Add `timeline.schema.json` or equivalent documented JSON schema.
7. Add provenance log schema.
8. Add tests that validate sample timeline/provenance objects.
9. Only after those pass, start runtime integration.

## Do not build yet

- Do not build a full video editor UI.
- Do not integrate CapCut/Premiere directly.
- Do not re-add Ken Burns.
- Do not rewrite `main.py` first.
- Do not scan or index personal media without explicit local-only storage rules and exclusion tests.
- Do not move any Drive files automatically.

## Safe next command for Codex

```text
Work only on Package 0 for Content Creator V2. Do not touch runtime code. Add public-safe Creation Gate and folder-role standards, then add timeline/provenance JSON schemas plus schema tests. Do not push to main, do not move Drive files, do not commit media/secrets/cache/embeddings/private exports.
```
