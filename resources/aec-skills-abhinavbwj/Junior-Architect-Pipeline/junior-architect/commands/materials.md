---
description: Visualisation and presentation: materials (RIBA stage 2, 3, 4; ceiling A3). A gated pipeline run with checker check_schedule.
argument-hint: [autonomy A0-A3] [notes]
---

You are running the **materials** task of the Junior Architect Pipeline. Engage the `visualisation` and `jap-core` skills, and delegate the work to the **visualiser** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start materials <level>`. The level is the one in the arguments, or the ceiling A3, and never above it.
2. **Inputs.** Confirm you have the material palette with real products, colours and finishes. If anything is missing, ask the junior.
3. **The junior first.** At A3 no prediction is required. If the junior runs it at A1 or A2, ask them: **Choose the palette with real samples, then compare the rendered colours with the samples.**
4. **The work.** The visualiser agent produces `.jap/runs/<run>/materials.csv`. Hosts: Revit, Rhino. Capabilities needed: create and assign materials; set texture mapping at true scale; sample colours from a product image; read material properties. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: texture scale wrong; generic materials left in the model; render colour far from the specified product.
5. **The check.** Run `check <run>/materials.csv <run>/model_materials.json materials` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
