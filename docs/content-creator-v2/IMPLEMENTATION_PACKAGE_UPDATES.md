# Content Creator V2 — Implementation Package Updates

Date: 2026-08-05
Runtime code changed: no.

## Package rule

Do not start Package 1 until Package 0 is complete and reviewed.

The current implementation should advance in small audited packages, not a broad rewrite.

## Updated package sequence

| Package | Name | Status | Scope |
|---|---|---:|---|
| Package 0 | Safety + Contracts Freeze | NEXT | Creation Gate, folder roles, duplicate policy, timeline/provenance schemas, schema tests. |
| Package 1 | Local Media Index Prototype | BLOCKED | Tiny fixture-only index, no personal media committed, scene detection/contact sheets. |
| Package 2 | Semantic Clip Search | BLOCKED | CLIP/OpenCLIP-style frame search + transcript search over indexed fixtures. |
| Package 3 | Script + Shot Plan Builder | BLOCKED | Convert idea/transcript into script and shot plan contract. |
| Package 4 | Timeline JSON Builder | BLOCKED | Generate validated timeline from shot plan + selected assets. |
| Package 5 | Human Approval Loop | BLOCKED | Extend approval handler to approve/patch timeline JSON. |
| Package 6 | Renderer Adapter | BLOCKED | FFmpeg/Remotion/Playwright adapters read timeline only. |
| Package 7 | Export + Provenance Receipt | BLOCKED | Export file + full provenance log + canonical save record. |
| Package 8 | UI/Review Experience | LATER | Timeline/contact-sheet review UI. Not required for first V2 proof. |

## Package 0 — exact scope

Allowed changes:

- Add Creation Gate documentation to public-safe standards.
- Add folder-role policy.
- Add duplicate-detection/duplicate-review policy.
- Add saved-item metadata schema.
- Add timeline JSON schema.
- Add provenance log schema.
- Add fixtures using synthetic/public-safe data only.
- Add tests that validate schemas.

Not allowed:

- runtime orchestration changes
- Drive moves
- file deletion
- archiving
- PR creation unless asked
- direct push to main
- media/cache/embedding commits
- personal/private media indexing
- Remotion integration

## Package 0 output files suggested

| File | Purpose |
|---|---|
| `docs/standards/CREATION_GATE.md` | Public-safe rule that Jarvis/Athena/Codex must follow. |
| `docs/content-creator-v2/schemas/creation_gate.schema.json` | Validation for pre-create decisions. |
| `docs/content-creator-v2/schemas/saved_item.schema.json` | Canonical saved-item metadata. |
| `docs/content-creator-v2/schemas/timeline.schema.json` | Timeline contract. |
| `docs/content-creator-v2/schemas/provenance.schema.json` | Export/provenance receipt. |
| `tests/fixtures/content_creator_v2/*.json` | Synthetic fixtures only. |
| `tests/test_content_creator_v2_schemas.py` | Schema validation tests. |

## Package 1 — local media index prototype

Start only after Package 0.

Goal:

- index a tiny fixture directory
- generate scene boundaries with PySceneDetect or stubbed fixtures
- generate contact sheet/proxy thumbnails
- store metadata in local SQLite
- keep cache outside Git

Do not index Priscila's real Apple Photos library in Package 1.

## Package 2 — semantic clip search

Goal:

- sample frames from indexed clips
- generate local embeddings or use a lightweight placeholder interface
- search by shot-plan visual query
- return ranked candidates with provenance and safety flags

Do not make CLIP/OpenCLIP a mandatory dependency until M3 8GB performance is tested.

## Package 3 — script + shot plan builder

Goal:

- transform idea/transcript into script and shot plan
- keep claims/source requirements explicit
- maintain content format registry awareness
- use confidence gates and manual-review routing

## Package 4 — timeline JSON builder

Goal:

- convert shot plan and selected semantic matches into valid timeline JSON
- validate before approval
- block invalid timelines

## Package 5 — approval loop

Goal:

- use current approval handler patterns
- collect approvals/revisions on timeline JSON
- patch plan/timeline, not only rendered post variants

## Package 6 — renderer adapter

Goal:

- renderer reads only approved timeline JSON
- first adapter should be simple FFmpeg/Playwright proof
- Remotion remains postponed until schema is stable

## Package 7 — export + provenance receipt

Goal:

- output video/image package
- write provenance receipt
- write saved-item metadata record
- enforce Creation Gate for final output folder

## Feature classification matrix

| Feature | Current source | Package | Classification |
|---|---|---:|---:|
| Creation Gate | missing | 0 | BUILD NEW |
| folder-role enum | missing | 0 | BUILD NEW |
| duplicate detection | partial/manual only | 0 | BUILD NEW |
| canonical saved-item metadata | missing | 0 | BUILD NEW |
| transcript verification | Phase 1 spec | 0/1 | EXTEND |
| classifier low-confidence routing | Phase 1 spec | 1/3 | EXTEND |
| capture metadata | `capture_pipeline.py` | 1/3 | REUSE + EXTEND |
| motion source provenance | `motion_sources.py` | 2 | ADAPT |
| scene detection/contact sheets | missing | 1 | BUILD NEW |
| semantic search | missing | 2 | BUILD NEW |
| script object | missing | 3 | BUILD NEW |
| shot plan object | missing | 3 | BUILD NEW |
| timeline JSON | missing | 4 | BUILD NEW |
| human approval | `approval_handler.py` | 5 | EXTEND |
| FFmpeg/Playwright rendering | manual docs/existing patterns | 6 | REUSE |
| Remotion rendering | frozen/legacy | 6+ | DO NOT TOUCH YET |
| editor UI | missing | 8 | REPLACE LATER |

## Exact next package to execute

```text
Package 0 — Safety + Contracts Freeze

Work only on docs, schemas, fixtures, and schema tests. Add Creation Gate and folder-role standards. Add JSON schemas for creation gate, saved item, timeline, and provenance. Add public-safe synthetic fixtures and tests. Do not touch runtime code. Do not push to main. Do not move Drive files. Do not commit personal media, cache, embeddings, tokens, secrets, OAuth data, private exports, or real videos.
```
