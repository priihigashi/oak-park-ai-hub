---
description: Drafting and documentation: detailing (RIBA stage 4; ceiling A1). A gated pipeline run with checker check_views.
argument-hint: [autonomy A0-A1] [notes]
---

You are running the **detailing** task of the Junior Architect Pipeline. Engage the `detailing` and `jap-core` skills, and delegate the work to the **documentation-lead** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start detailing <level>`. The level is the one in the arguments, or the ceiling A1, and never above it.
2. **Inputs.** Confirm you have the wall, floor and roof build-ups (layers, thicknesses, materials) and the details list. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Draw the junction by hand first: the line of insulation, the airtight layer, the drainage path.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The documentation-lead agent produces `.jap/runs/<run>/detail_views.json`. Hosts: Revit, Rhino. Capabilities needed: create wall sections and drafting views; place detail components, repeating details and insulation; draw filled regions and detail lines; cut sections and hatch. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: insulation line broken at the junction; airtight layer discontinuous; build-up thicknesses differ from the wall type; detail not referenced from the plan.
5. **The check.** Run `check <run>/detail_views.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
