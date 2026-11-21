---
description: Visualisation and presentation: rendering (RIBA stage 2, 3, 4; ceiling A2). A gated pipeline run with checker check_render.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **rendering** task of the Junior Architect Pipeline. Engage the `visualisation` and `jap-core` skills, and delegate the work to the **visualiser** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start rendering <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the approved cameras, the materials, the site context and the date and time of each view. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Write what each image must make a viewer understand, then check the render against it.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The visualiser agent produces `.jap/runs/<run>/renders.json`. Hosts: Rhino, Revit, Blender. Capabilities needed: set environment and sun; set camera; render stills; run long render jobs. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: sun at an impossible position for the site; context missing or invented; people at the wrong scale; image sharper or emptier than the place will ever be.
5. **The check.** Run `check <run>/renders.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
