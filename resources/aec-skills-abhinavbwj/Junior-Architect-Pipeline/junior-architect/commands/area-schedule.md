---
description: Schedules and quantities: area schedule (RIBA stage 2, 3, 4; ceiling A2). A gated pipeline run with checker check_areas.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **area-schedule** task of the Junior Architect Pipeline. Engage the `area-measurement` and `jap-core` skills, and delegate the work to the **quantity-scheduler** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start area-schedule <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the model and the brief targets (targets.csv: room,target_m2). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Estimate the total and the three largest deviations from the brief before the run.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The quantity-scheduler agent produces `.jap/runs/<run>/area_schedule.csv`. Hosts: Revit, Rhino. Capabilities needed: read room boundaries as polylines with units; read area plans; measure closed curves. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: feet versus metres; wrong area definition (centreline versus internal face); open or duplicate boundaries; nested rooms counted twice; arcs under-measured.
5. **The check.** Run `check <run>/rooms.json targets.csv` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
