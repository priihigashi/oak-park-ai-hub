---
name: model-audit
description: Auditing model health in Revit or Rhino before documentation or exchange. Covers rooms, levels and layers, units, marks, views and sheets, links, warnings, and the audit export format. Use for model-audit tasks.
---

# Model audit

## Export for `check_schedule ... audit`
`model_audit.json` is a list of elements, each with `id` and `problems` (a list of strings). The checker reports every problem.

## What to check

| Area | Revit | Rhino |
|---|---|---|
| Rooms and spaces | Unplaced, not enclosed, redundant | Room curves open, duplicated or off-layer |
| Levels and layers | Elements on the wrong level | Objects on the wrong layer, or on layer 0 / Default |
| Units and coordinates | Project units, survey and project base points, shared coordinates | Document units, model origin far from geometry |
| Identity | Duplicate marks and numbers | Duplicate names or object ids in schedules |
| Views and sheets | Views not on sheets, sheets with no views, unused view templates | Named views and layouts out of date |
| Links | Unloaded or unresolved links | Unresolved block references and worksessions |
| Warnings | Exported and grouped by type, with counts | n/a |

## The junior's step
Predict the three worst problems before the audit runs. Comparing the prediction with the audit trains the eye for model health, which seniors use on every review.
