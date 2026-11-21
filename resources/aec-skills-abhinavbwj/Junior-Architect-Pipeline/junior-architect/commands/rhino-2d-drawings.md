---
description: Drafting and documentation: rhino 2d drawings (RIBA stage 2, 3, 4; ceiling A2). A gated pipeline run with checker check_dxf.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **rhino-2d-drawings** task of the Junior Architect Pipeline. Engage the `drafting-standards` and `jap-core` skills, and delegate the work to the **cad-drafter** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start rhino-2d-drawings <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the 3D model, the drawings to extract (plans, sections, elevations) and the CAD standard in project.json cad. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Decide the line weights for cut, beyond and below before the drawing is extracted.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The cad-drafter agent produces `.jap/runs/<run>/drawing.dxf`. Hosts: Rhino. Capabilities needed: create layers to the CAD standard; cut sections and clipping planes; extract 2D linework (Make2D); hatch, dimension and add text; export DXF and DWG. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: entities on layer 0; layers off the convention; units not millimetres; text heights off the series; Make2D output not cleaned (duplicate and hidden lines).
5. **The check.** Run `check <run>/drawing.dxf` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
