---
description: Drafting and documentation: dwg export (RIBA stage 3, 4, 5; ceiling A3). A gated pipeline run with checker check_dxf.
argument-hint: [autonomy A0-A3] [notes]
---

You are running the **dwg-export** task of the Junior Architect Pipeline. Engage the `drafting-standards` and `jap-core` skills, and delegate the work to the **cad-drafter** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start dwg-export <level>`. The level is the one in the arguments, or the ceiling A3, and never above it.
2. **Inputs.** Confirm you have the views or sheets to exchange and the receiving party's CAD standard. If anything is missing, ask the junior.
3. **The junior first.** At A3 no prediction is required. If the junior runs it at A1 or A2, ask them: **Open the export in a CAD viewer and check one layer and one dimension yourself.**
4. **The work.** The cad-drafter agent produces `.jap/runs/<run>/export.dxf`. Hosts: Revit, Rhino. Capabilities needed: export DWG and DXF with a layer mapping. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: layer mapping lost; units changed on export; xrefs bound or missing; text exploded.
5. **The check.** Run `check <run>/export.dxf` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
