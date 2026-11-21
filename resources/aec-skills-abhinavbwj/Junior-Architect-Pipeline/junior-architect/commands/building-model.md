---
description: 3D modelling, BIM and Grasshopper: building model (RIBA stage 2, 3, 4; ceiling A2). A gated pipeline run with checker check_areas.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **building-model** task of the Junior Architect Pipeline. Engage the `bim-production` and `jap-core` skills, and delegate the work to the **bim-modeller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start building-model <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the approved plan (sketch, DWG or Rhino plan), the levels and grids, the room targets (targets.csv). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Mark on the plan where you expect the model to disagree with the sketch (walls that do not close, rooms that will not bound).** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The bim-modeller agent produces `.jap/runs/<run>/rooms.json`. Hosts: Revit, Rhino. Capabilities needed: link or import a CAD plan; create joined walls, floors, ceilings and roofs; create openings; place doors and windows in host walls; create and read rooms; read model warnings. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: walls that do not join, so rooms will not bound; walls drawn to centreline where the plan measures faces; doors placed in the wrong host or swing; rooms placed in unbounded spaces.
5. **The check.** Run `check <run>/rooms.json targets.csv` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
