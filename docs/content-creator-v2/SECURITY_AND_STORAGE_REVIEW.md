# Content Creator V2 — Security and Storage Review

Date: 2026-08-05
Runtime code changed: no.

## Executive conclusion

The current repo already contains some strong storage rules, especially shared-drive routing and public/private rule separation. The missing security layer is a formal Creation Gate with folder-role refusal and duplicate-review routing.

The most important fix is to stop treating any available folder as a valid destination. Destination role must be checked before saving.

## Existing good controls

| Control | Status | Notes |
|---|---:|---|
| Public/private agent rule split | PRESENT | Public `AGENTS.md` points private rules to private repo and warns not to add private details back. |
| Shared Drive default | PRESENT | Existing rules require shared drive usage and `supportsAllDrives=True`. |
| News vs Marketing routing | PRESENT | Existing rules prohibit news content in Marketing Drive. |
| Flow doc logging | PRESENT | New flow/master/process docs must be logged. |
| Spreadsheet hub logging | PRESENT | New spreadsheets/tabs must be logged. |
| Script editing safety | PRESENT | Full-file read and surgical edits required before script changes. |
| Secret value guessing refusal | PRESENT | Rules warn not to guess GitHub secret values. |
| private media in public repo | PARTIAL | Public/private split exists; V2 needs explicit no-media/no-embedding rule. |

## Missing controls

| Missing control | Risk | Required fix |
|---|---|---|
| folder-role enum | live files can land in backup/archive/system folders | Add `ACTIVE`, `REFERENCE`, `ARCHIVE`, `BACKUP`, `SYSTEM`. |
| backup/archive refusal | workspace mess and accidental live work in reset folders | Refuse writes unless explicit archive action. |
| Mac reset/migration folder classification | backup folders can be mistaken for normal workspace | Default reset/migration/export folders to `BACKUP`. |
| duplicate pre-create search | parallel docs/folders/trackers | Search exact/similar names and registries first. |
| Duplicate Review route | uncertain items become more mess | Route uncertain items to Duplicate Review instead of creating. |
| Canonical Home field | hard to recover where a product/doc truly lives | Add to major products/docs. |
| saved-item reason | future agents cannot understand filing choice | Record reason for location. |
| no embeddings/cache in git rule | private media leakage risk | Explicitly ban committing embeddings/cache/thumbnails/transcripts from private media. |

## Folder role policy

### `ACTIVE`

Live canonical work location.

Writes allowed only after Creation Gate passes.

### `REFERENCE`

Reference/library/source material.

Writes allowed only when item is reference material and Creation Gate passes.

### `ARCHIVE`

Retired/non-live storage.

Writes refused unless user explicitly says the action is archival.

### `BACKUP`

Recovery-only location.

Includes folders created by:

- Mac reset
- migration
- export
- Time Machine or backup process
- emergency restore
- old workspace copy

Writes refused for live work.

If live files exist there, flag for rescue/inventory; do not continue using it.

### `SYSTEM`

Application/tool/internal paths.

Writes only allowed for approved automation, cache, or config operations, and never as canonical user-facing storage.

## Mandatory saved-item record

Every saved item must record:

```json
{
  "saved_item_id": "string",
  "name": "string",
  "item_type": "product|flow|doc|tracker|asset|task|export|other",
  "canonical_owner_product": "string",
  "canonical_folder": "string",
  "folder_role": "ACTIVE|REFERENCE|ARCHIVE|BACKUP|SYSTEM",
  "related_focus_row": "string|null",
  "related_github_doc_repo": "string|null",
  "related_flow_plans_row": "string|null",
  "related_drive_map_row": "string|null",
  "duplicate_review_status": "not_needed|pending|resolved",
  "save_reason": "string",
  "created_or_updated_by": "Jarvis/Athena/Codex/manual",
  "created_or_updated_at": "ISO-8601"
}
```

## Duplicate review policy

Route to Duplicate Review when:

- same or similar doc/folder/product exists
- canonical home is missing/unknown
- target folder role is unknown
- target is backup/archive but item looks live
- two trackers appear to describe same product/flow
- file name indicates copy/export/backup/migration/reset
- user request is ambiguous about whether to create or update

Do not automatically delete, move, or archive duplicates.

## Git safety policy

Never commit:

- personal media
- real videos
- local cache
- embeddings
- thumbnails/contact sheets generated from private media
- exported private documents
- secrets
- OAuth tokens
- API keys
- cookies
- `.env`
- downloaded private attachments

If sample media is needed, use synthetic fixtures or public test assets with provenance.

## Renderer/export safety

Renderer must not run unless:

1. timeline schema is valid
2. asset references are allowed
3. approval state permits render/export
4. output canonical folder passed Creation Gate
5. provenance log target is known

## Immediate standard to add

Add this public-safe rule to the Jarvis/Athena standards surface:

```text
CREATION GATE — MANDATORY PRE-SAVE/PRE-CREATE RULE
Before creating, moving, saving, or routing any file/folder/doc/tracker/asset/task, search the canonical registries and exact/similar existing names; classify target folder role as ACTIVE, REFERENCE, ARCHIVE, BACKUP, or SYSTEM; refuse BACKUP/ARCHIVE live writes; route uncertain/duplicate items to Duplicate Review; record canonical owner/product, canonical folder, related Focus row, related GitHub doc/repo, folder role, and reason saved there.
```

## Risk level after documentation

Current risk: `MEDIUM-HIGH` until runtime standards/tests enforce this.

After Package 0 standards/schema/tests: `MEDIUM`.

After runtime Creation Gate enforcement: `LOW-MEDIUM`.
