---
name: drawing-qa
description: Checking drawing sets. Covers title blocks, ISO 19650 container naming and status codes, references between sheets, consistency between tags and schedules, and the redline format. Use for drawing-qa tasks and before any issue of drawings.
---

# Drawing QA

## Naming and status
The template in `.jap/project.json` follows the ISO 19650 UK National Annex field order:

`Project-Originator-Volume/System-Level-Type-Role-Number`, for example `PRJ01-XYZ-00-GF-DR-A-1001`.

Status codes in the template:

| Code | Meaning |
|---|---|
| S0 | Work in progress |
| S1 | Suitable for coordination |
| S2 | Suitable for information |
| S3 | Suitable for review and comment |
| S4 | Suitable for stage approval |
| S6, S7 | Information-model authorisation |
| A1 to An | Authorised and accepted |
| B1 to Bn | Partially signed off, with comments |
| CR | As-constructed record |

Offices outside the UK, and many inside it, use their own conventions. Replace the pattern and the list with the office's own.

## What `check_sheets` checks
Input is `sheets.csv`: number, title, revision, status, drawn_by, checked_by, date, references. The checker flags:
- duplicate numbers;
- names that break the convention;
- unknown status codes;
- empty title-block fields;
- references to sheets not in the register;
- sheets drawn and checked by the same person.

## What only a person can check
- Coordination clashes.
- Design intent.
- Buildability.
- Whether a dimension string closes.
- Whether a detail matches its callout.

The drawing-checker agent lists these as `for the junior`. It never resolves them itself.

## The redline
`redline.csv` columns: item, sheet, location, issue, evidence, suggested fix, confidence. The junior accepts or rejects each item with a one-line reason. Low-confidence items are marked as such.
