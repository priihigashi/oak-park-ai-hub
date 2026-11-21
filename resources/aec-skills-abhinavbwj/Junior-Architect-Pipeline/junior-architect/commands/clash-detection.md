---
description: Analysis, coordination and exchange: clash detection (RIBA stage 3, 4; ceiling A2). A gated pipeline run with checker check_clash.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **clash-detection** task of the Junior Architect Pipeline. Engage the `bim-coordination` and `jap-core` skills, and delegate the work to the **bim-coordinator** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start clash-detection <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the federated model (linked discipline models) and the clash matrix (which categories against which, tolerance). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Predict the two discipline pairs with the most clashes before the run.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The bim-coordinator agent produces `.jap/runs/<run>/clashes.json`. Hosts: Revit. Capabilities needed: link discipline models; run clash detection between categories; zoom to and capture clashing elements. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: tolerance so tight that noise hides real clashes; clashes closed without an owner; duplicate clashes counted separately.
5. **The check.** Run `check <run>/clashes.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
