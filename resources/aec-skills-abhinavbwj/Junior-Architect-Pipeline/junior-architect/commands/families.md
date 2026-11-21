---
description: 3D modelling, BIM and Grasshopper: families (RIBA stage 3, 4; ceiling A2). A gated pipeline run with checker check_schedule.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **families** task of the Junior Architect Pipeline. Engage the `bim-production` and `jap-core` skills, and delegate the work to the **bim-modeller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start families <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the family brief: category, parameters, types and naming per the office standard (required_fields.families). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Sketch the family's reference planes and parameters before the agent builds it.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The bim-modeller agent produces `.jap/runs/<run>/families.csv`. Hosts: Revit. Capabilities needed: create and edit families from templates; add family parameters; load families; read family parameters. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: geometry not locked to reference planes, so it breaks on flex; wrong category, so it schedules wrongly; type names off the naming convention.
5. **The check.** Run `check <run>/families.csv <run>/model_families.json families` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
