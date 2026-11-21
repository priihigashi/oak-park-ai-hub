---
description: Regulation and envelope: regulation check (RIBA stage 2, 3, 4; ceiling A1). A gated pipeline run with checker check_metrics.
argument-hint: [autonomy A0-A1] [notes]
---

You are running the **regulation-check** task of the Junior Architect Pipeline. Engage the `massing-and-envelope` and `jap-core` skills, and delegate the work to the **bim-modeller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start regulation-check <level>`. The level is the one in the arguments, or the ceiling A1, and never above it.
2. **Inputs.** Confirm you have the design model and regulation_rules.json (height, coverage, FAR, setbacks, parking, outdoor space) with sources. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Name the rule you expect the design to fail, and by how much.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The bim-modeller agent produces `.jap/runs/<run>/regulation_metrics.json`. Hosts: Revit, Rhino. Capabilities needed: read room and area boundaries; measure heights, footprints and floor areas; read schedules and quantities. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: measured to a different area standard than the rule; rule paraphrased into a different limit; compliance claimed from an unchecked number.
5. **The check.** Run `check <run>/regulation_metrics.json <run>/regulation_rules.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
