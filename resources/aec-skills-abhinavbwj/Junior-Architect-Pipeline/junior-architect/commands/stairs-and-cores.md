---
description: 3D modelling, BIM and Grasshopper: stairs and cores (RIBA stage 3, 4; ceiling A2). A gated pipeline run with checker check_stairs.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **stairs-and-cores** task of the Junior Architect Pipeline. Engage the `stairs-and-cores` and `jap-core` skills, and delegate the work to the **bim-modeller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start stairs-and-cores <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the core layout, floor-to-floor heights and the stair rules of the code in force (set stair_rules in project.json). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Calculate the number of risers, the riser height and the going by hand from the floor-to-floor height before the stair is modelled.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The bim-modeller agent produces `.jap/runs/<run>/stairs.json`. Hosts: Revit, Rhino. Capabilities needed: create stairs and railings; create shafts; read stair parameters (risers, goings, widths, headroom); create sections. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: 2R+G outside the comfort range; uneven risers at the top or bottom; headroom clash under the flight above; too many risers in one flight.
5. **The check.** Run `check <run>/stairs.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
