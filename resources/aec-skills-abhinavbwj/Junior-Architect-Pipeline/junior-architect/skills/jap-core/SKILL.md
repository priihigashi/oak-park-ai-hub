---
name: jap-core
description: The operating model of the Junior Architect Pipeline. Covers the run cycle, autonomy levels A0-A4, the gates, the verification rules and the learning loop. Use for any junior-architect production task run through the pipeline, and whenever a run is open in .jap/.
---

# Junior Architect Pipeline: operating model

## Why it is built this way
Architecture trains seniors through production work: brief digests, code notes, schedules, redlines, minutes. Schön called design "a reflective conversation with the situation". The junior acts, the drawing talks back, and the junior reframes.

A pipeline that only automates that work removes the conversation. This pipeline automates the clerical part and keeps the conversation with the junior.

## The run cycle
1. `start <task> [level]`: opens `.jap/runs/<run>/`. The level is capped at the task's ceiling in `pipeline.json`.
2. **Prediction** (A1, A2): the junior writes what they expect before the agent works. Hooks block model access and the deliverable until it exists.
3. **Work:** the task's agent produces the deliverable in the run folder, from raw exports, never retyped.
4. **Check:** the task's deterministic checker recomputes everything and writes `report.json`. Only the checker writes it.
5. **Review:** the junior accepts or rejects each finding with a reason and adds `found:` lines for anything the checker missed.
6. `close`: appends to `.jap/learning_log.csv`.

## Autonomy levels

| Level | Who does what |
|---|---|
| A0 | The junior does the task. The agent answers questions only. |
| A1 | The agent drafts after the junior's prediction. The junior rewrites or approves every line. |
| A2 | The agent executes, checks gate the output, and the junior reviews the redline. |
| A3 | The agent executes and checks. The junior signs off a sample of at least 20%. |
| A4 | Fully automatic. No task uses it by default. |

Code research, planning constraints, specification and RFIs have an A1 ceiling. A fluent answer can still be wrong on a threshold, and in the one AEC code benchmark (Hong Kong fire code, 2026) the best model reached about 66% expert-rated accuracy on open questions.

## The gates

| Gate | Rule |
|---|---|
| G1 | Claude never writes `prediction.md` or `review.md`, by any tool. |
| G2 | Only the pipeline scripts write `report.json`, `run.json`, `state.json` and the learning log. |
| G3 | At A1 and A2, no MCP call and no write into the run folder happens before the prediction. |
| G4 | Claude cannot finish while a deliverable exists without a checker report. |
| G5 | The checkers and gates are read-only during a run. |

## Verification rules
- Every number is recomputed by the checker from raw data. Never present a number the checker has not confirmed.
- Units are converted once, at the boundary, in one place. Revit stores lengths in feet internally. A result off by about 10.764, 92,903 or 1,000,000 is a units error.
- A code clause is quoted verbatim with clause, edition and jurisdiction, from a supplied document. A paraphrase is unverified.
- A failing check is reported as failing.
- Escalate code compliance, fire, structure, contract and cost to a named senior.

## The learning loop
The prediction error and the junior's own findings over runs are the apprenticeship record. The `mentor` agent reads them and moves tasks up or down the autonomy levels.
