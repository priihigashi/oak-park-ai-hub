# Content Creator V2 — Architecture Decisions

Date: 2026-08-05
Status: proposed freeze candidates
Runtime code changed: no.

## AD-001 — Creation Gate is mandatory before save/create/move

Decision: `ACCEPT`

Before any file, folder, doc, tracker, or asset is created/moved/saved, Jarvis/Athena must run the Creation Gate.

Required checks:

1. Flow Plans Tracker — Master Index
2. Drive Map — ALL DRIVES
3. Drive Map — Marketing
4. Drive Map — OPC where relevant
5. Focus rows
6. GitHub docs
7. Google Drive exact and similar names
8. target folder role
9. duplicate/similar-item review

Required answers:

- Is this an existing product, flow, doc, tracker, asset, or task?
- Is there already a canonical row?
- Is there already a canonical physical location?
- Is the target location `ACTIVE`, `REFERENCE`, `ARCHIVE`, `BACKUP`, or `SYSTEM`?
- If similar files exist, should this update/link an existing item instead of creating a new one?

Consequence: uncertain items route to Duplicate Review, not a parallel structure.

## AD-002 — Folder roles are first-class metadata

Decision: `ACCEPT`

Every major folder/location must be classified as one of:

| Role | Meaning | Write policy |
|---|---|---|
| `ACTIVE` | Canonical live working home | Writes allowed after Creation Gate. |
| `REFERENCE` | Source/library/reference material | Writes allowed only for reference additions after Creation Gate. |
| `ARCHIVE` | Retired/non-live storage | Refuse unless user explicitly requests archival action. |
| `BACKUP` | Recovery-only location, including Mac reset/migration/export backups | Read-only; never live filing. |
| `SYSTEM` | Tool/application/internal path | Writes only by explicitly approved automation. |

Mac reset, migration, export, and backup-created folders default to `BACKUP` unless explicitly reclassified.

## AD-003 — Backup and archive folders are not live homes

Decision: `ACCEPT`

Jarvis/Athena must refuse to save new live files into `BACKUP` or `ARCHIVE`.

If a live file exists there, flag it as:

```json
{
  "status": "RESCUE_REQUIRED",
  "reason": "Live item found in backup/archive location",
  "recommended_action": "inventory_and_link_to_canonical_home"
}
```

No automatic move/delete/archive is allowed.

## AD-004 — Timeline JSON is the contract between modules

Decision: `ACCEPT`

Timeline JSON becomes the boundary between:

- Script
- Shot Plan
- Semantic Clip Search
- Human Approval
- Renderer
- Export / Provenance Log

No renderer should accept loose ad hoc inputs once V2 starts.

Minimum timeline sections:

```json
{
  "project": {},
  "script": {},
  "shot_plan": [],
  "assets": [],
  "semantic_matches": [],
  "tracks": [],
  "approval": {},
  "export_settings": {},
  "provenance": {}
}
```

## AD-005 — AI plans; deterministic tools render

Decision: `ACCEPT`

LLMs can classify, script, propose shots, rank clips, and explain decisions.

LLMs must not directly render opaque video output or silently mutate assets.

Render/export should be deterministic through validated local tools such as FFmpeg, Remotion, Playwright, or approved equivalents.

## AD-006 — Human approval comes before render/export

Decision: `ACCEPT`

Approval state belongs to the timeline contract.

The human should approve:

1. script
2. shot plan
3. selected clips/assets
4. timeline timing/layout
5. final export if needed

Do not spend render/export work on an unapproved timeline except for explicit preview/proof generation.

## AD-007 — Local/exported media index before cloud source sprawl

Decision: `ACCEPT`

Content Creator V2 should prioritize local-first/private-safe media:

1. exported Apple Photos / local folders / curated project media
2. existing clip collections
3. approved public sources with provenance
4. commercial editor export/import only after core contract works

Do not rebuild the retired 8-tier source cascade.

## AD-008 — Apple Photos integration must be export-driven

Decision: `ACCEPT`

Do not read `Photos.sqlite` directly as a production dependency.

Use export-driven workflows with metadata sidecars where possible, so the index does not depend on Apple private database internals.

## AD-009 — Every saved item has canonical metadata

Decision: `ACCEPT`

Every saved item must record:

- canonical owner/product
- canonical folder
- folder role
- related Focus row
- related GitHub doc/repo
- related Flow Plans Tracker row if applicable
- related Drive Map row if applicable
- reason it was saved there
- duplicate review status
- provenance/source

## AD-010 — Do not start Package 1 yet

Decision: `ACCEPT`

Package 1 is blocked until Package 0 freezes:

- Creation Gate
- folder role policy
- duplicate routing
- canonical metadata schema
- timeline schema
- provenance schema
- contract tests

## Feature classification

| Feature | Classification |
|---|---:|
| Creation Gate | BUILD NEW |
| folder role awareness | BUILD NEW |
| backup/archive refusal | BUILD NEW |
| duplicate detection before create | BUILD NEW |
| Duplicate Review routing | BUILD NEW |
| Canonical Home field | BUILD NEW |
| saved-item metadata | BUILD NEW |
| current capture pipeline | REUSE + EXTEND |
| current motion source cascade | ADAPT |
| current approval handler | EXTEND |
| current manual builder docs | REUSE |
| current Phase 1 transcript/classifier spec | EXTEND |
| runtime code changes | DO NOT TOUCH YET |
| Remotion integration | DO NOT TOUCH YET |
| full editor UI | REPLACE LATER |
