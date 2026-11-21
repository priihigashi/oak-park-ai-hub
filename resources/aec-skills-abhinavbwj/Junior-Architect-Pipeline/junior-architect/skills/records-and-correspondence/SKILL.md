---
name: records-and-correspondence
description: The project record. Covers meeting minutes, sheet registers and transmittals, with the check_minutes and check_sheets formats. Use for meeting-minutes and sheet-register tasks.
---

# Records and correspondence

## Minutes
- `## Decisions`: what was decided and by whom.
- `## Actions`: a table with Action | Owner | Due (YYYY-MM-DD).

`check_minutes` checks:
- every action has an owner and an ISO date;
- every quote attributed to a person appears in `transcript.txt`.

The junior flags every decision that changes scope, cost or programme. Those are the decisions that matter in a dispute.

## Sheet registers and transmittals
- **The register:** one row per sheet with number, title, revision, status, drawn_by, checked_by, date, references.
- **Each issue:** a transmittal listing the sheets, their revisions and status codes, the recipients and the purpose of the issue.
- **Checks:** `check_sheets` applies the naming convention and status codes from `.jap/project.json`.
- **The junior's step:** confirm the revision and status of every sheet issued for construction.

## Dates and names
Write dates as YYYY-MM-DD. Use full names and organisations on first mention. Never invent an attendee, a decision or a date.
