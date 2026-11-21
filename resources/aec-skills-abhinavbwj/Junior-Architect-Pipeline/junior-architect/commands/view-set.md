---
description: Drafting and documentation: view set (RIBA stage 3, 4; ceiling A3). A gated pipeline run with checker check_views.
argument-hint: [autonomy A0-A3] [notes]
---

You are running the **view-set** task of the Junior Architect Pipeline. Engage the `drawings-and-sheets` and `jap-core` skills, and delegate the work to the **documentation-lead** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start view-set <level>`. The level is the one in the arguments, or the ceiling A3, and never above it.
2. **Inputs.** Confirm you have the drawing list for the stage (levels, sections, elevations, scales in project.json view_requirements). If anything is missing, ask the junior.
3. **The junior first.** At A3 no prediction is required. If the junior runs it at A1 or A2, ask them: **Mark the section lines on the plan yourself: where a section cuts decides what it explains.**
4. **The work.** The documentation-lead agent produces `.jap/runs/<run>/views.json`. Hosts: Revit. Capabilities needed: create plans per level, sections, elevations, callouts and 3D views; set crops and scope boxes; apply view templates and filters; rename and list views. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: sections that cut nothing informative; views without templates; duplicate or default names; wrong scale for the stage.
5. **The check.** Run `check <run>/views.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
