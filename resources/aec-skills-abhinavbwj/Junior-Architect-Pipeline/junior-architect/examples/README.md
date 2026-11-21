# Examples: seeded faults and expected results

Each folder holds small inputs with known faults. Run them after installing, or after changing a checker or an MCP server, and compare the output with the expected results below.

```
cd <any empty test folder>
node <plugin>/scripts/jap.js init
node <plugin>/scripts/jap.js start <task>
node <plugin>/scripts/jap.js predict "test"    # you, the junior
node <plugin>/scripts/jap.js check <inputs>
```

## area-schedule
20 rooms, 10 seeded faults: `rooms.json` (mm) and `targets.csv`.

**Expected: FAIL, 9 errors and 2 warnings.** Every seeded fault is caught:

| Seeded fault | What the checker reports |
|---|---|
| A room drawn in feet but declared as mm | `unit-trap` |
| An open curve | `open-boundary` |
| A duplicate | `duplicate` |
| A room on the wrong layer | `wrong-layer` |
| A name typo | `name-typo` |
| An arc-walled room | `arcs` (warning) |
| A store nested in the library | `nested` |
| A room drawn to the centreline | `area-definition`, plus a +9.2% deviation |
| A room missing from the brief | `no-target` (warning) |
| A room 6% under target | `deviation` |

## door-schedule
`door_schedule.csv` and `model_doors.json`. **Expected: FAIL, 5 errors.**
- duplicate mark D02
- D04 missing from the schedule
- D05 missing from the model
- empty ironmongery set on D03
- D03 fire rating FD60S in the schedule against FD30S in the model

## code-research
`code_notes.md` and `code_text.txt`. **Expected: FAIL, 4 errors.**
- a quote with the limit changed from 45 m to 60 m
- a clause with no edition and no jurisdiction
- a quote that is not in the code

## drawing-qa
`sheets.csv`. **Expected: FAIL, 5 errors.**
- a dead reference
- a sheet drawn and checked by the same person
- an empty date
- status S9
- a name outside the convention

## meeting-minutes
`minutes.md` and `transcript.txt`. **Expected: FAIL, 2 errors.**
- an action with no owner
- a due date of "next week"

## brief-digest
`brief_digest.md` and `brief.txt`. **Expected: FAIL, 2 errors.**
- 100 bicycles where the brief says 80
- an invented rooftop garden with no quote

## spec-section
`spec_section.md`, `standards_register.csv` and `ironmongery.csv`. **Expected: FAIL, 2 errors.**
- EN 1935 is not in the register
- product IS-9 has no schedule item

## rfi-response
`rfi_response.md`, checked against `../drawing-qa/sheets.csv`. **Expected: FAIL, 3 errors.**
- a superseded revision (P02, current P03)
- a dead sheet reference
- contractual liability wording

---
Junior Architect Pipeline by Abhinav Bhardwaj. MIT licence.
