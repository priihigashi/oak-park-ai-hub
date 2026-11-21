---
description: 3D modelling, BIM and Grasshopper: bim setup (RIBA stage 2, 3; ceiling A3). A gated pipeline run with checker check_schedule.
argument-hint: [autonomy A0-A3] [notes]
---

You are running the **bim-setup** task of the Junior Architect Pipeline. Engage the `bim-production` and `jap-core` skills, and delegate the work to the **bim-modeller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start bim-setup <level>`. The level is the one in the arguments, or the ceiling A3, and never above it.
2. **Inputs.** Confirm you have the levels and grids schedule (names, elevations, spacing), the office template and project info. If anything is missing, ask the junior.
3. **The junior first.** At A3 no prediction is required. If the junior runs it at A1 or A2, ask them: **Write the floor-to-floor heights and structural zone before the levels are created.**
4. **The work.** The bim-modeller agent produces `.jap/runs/<run>/levels_grids.csv`. Hosts: Revit. Capabilities needed: set project units and information; create levels and grids; create wall, floor and roof types with layers; apply view templates; organise the project browser; set up worksets. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: levels named against the office convention; grid spacing in the wrong units; no shared coordinates; types created without materials or layers.
5. **The check.** Run `check <run>/levels_grids.csv <run>/model_levels_grids.json levels` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
