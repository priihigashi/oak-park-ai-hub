---
name: specifications
description: Drafting specification sections linked to schedules and a standards register. Covers NBS, CSI MasterFormat, Uniclass 2015, performance versus prescriptive clauses, and the check_spec format. Use for spec-section tasks.
---

# Specifications

## Systems
Use the office's system and never mix systems in one specification:

| System | Where | Structure |
|---|---|---|
| NBS | UK | Classified by Uniclass 2015 |
| CSI MasterFormat | North America | Divisions 00 to 49 |
| National systems | Other countries | For example STLB-Bau in Germany, NATSPEC in Australia |

## The standards register
`standards_register.csv` columns: code, edition, status, replaced_by. Only standards in the register may be cited. `check_spec` flags:
- any standard cited that is not in the register;
- any standard marked withdrawn or superseded.

The junior or the librarian keeps the register current. The agent never adds to it from memory.

## Linking to schedules
Tag every product line `[P:<schedule id>]`. `check_spec` flags product lines that have no schedule item: specified products nobody scheduled.

## Performance and prescription
A performance clause states what the element must achieve, for example a fire resistance, an acoustic rating or a U-value. A prescriptive clause names a product or method. Where both appear, the named product must meet the stated performance.

The junior writes the performance clause by hand once per section type. That clause is where specification judgement is learned.
