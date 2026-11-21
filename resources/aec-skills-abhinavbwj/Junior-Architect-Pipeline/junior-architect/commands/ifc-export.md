---
description: Analysis, coordination and exchange: ifc export (RIBA stage 3, 4, 5, 6; ceiling A3). A gated pipeline run with checker check_ifc.
argument-hint: [autonomy A0-A3] [notes]
---

You are running the **ifc-export** task of the Junior Architect Pipeline. Engage the `bim-coordination` and `jap-core` skills, and delegate the work to the **bim-coordinator** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start ifc-export <level>`. The level is the one in the arguments, or the ceiling A3, and never above it.
2. **Inputs.** Confirm you have the model, the exchange requirements (schema, required entities) and the counts from the model (expected_counts.json). If anything is missing, ask the junior.
3. **The junior first.** At A3 no prediction is required. If the junior runs it at A1 or A2, ask them: **Open the IFC in a free viewer and check one storey and one door by hand.**
4. **The work.** The bim-coordinator agent produces `.jap/runs/<run>/model.ifc`. Hosts: Revit. Capabilities needed: export IFC with a category mapping; read element statistics and levels. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: elements exported as IfcBuildingElementProxy; storeys missing or renamed; spaces without names; units lost.
5. **The check.** Run `check <run>/model.ifc <run>/expected_counts.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
