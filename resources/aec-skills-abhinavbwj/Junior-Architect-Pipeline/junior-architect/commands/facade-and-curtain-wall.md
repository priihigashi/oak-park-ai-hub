---
description: 3D modelling, BIM and Grasshopper: facade and curtain wall (RIBA stage 3, 4; ceiling A2). A gated pipeline run with checker check_panels.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **facade-and-curtain-wall** task of the Junior Architect Pipeline. Engage the `facades-and-panels` and `jap-core` skills, and delegate the work to the **bim-modeller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start facade-and-curtain-wall <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the facade strategy (module, glazing ratio, panel limits in project.json fabrication). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Choose the module and predict how many unique panel types it produces.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The bim-modeller agent produces `.jap/runs/<run>/panels.json`. Hosts: Revit, Rhino, Grasshopper. Capabilities needed: create curtain walls and grids; panelise faces; divide curves and surfaces; read panel sizes and planarity. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: panels beyond transport or glass-size limits; slivers at corners; too many unique types; double-curved panels assumed flat.
5. **The check.** Run `check <run>/panels.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
