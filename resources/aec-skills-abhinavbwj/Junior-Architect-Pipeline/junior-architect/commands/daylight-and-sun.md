---
description: Analysis, coordination and exchange: daylight and sun (RIBA stage 2, 3, 4; ceiling A2). A gated pipeline run with checker check_metrics.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **daylight-and-sun** task of the Junior Architect Pipeline. Engage the `analysis` and `jap-core` skills, and delegate the work to the **analyst** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start daylight-and-sun <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the model, the daylight and sun requirements of the code in force (daylight_rules.json with sources). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Predict the three worst-lit rooms before the analysis runs.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The analyst agent produces `.jap/runs/<run>/daylight_metrics.json`. Hosts: Revit, Rhino. Capabilities needed: compute window-to-floor ratios per room; run sun-hour or daylight analysis; read room areas. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: window-to-floor ratio used where the code asks for a daylight factor; obstruction from neighbours omitted; metric from the wrong standard.
5. **The check.** Run `check <run>/daylight_metrics.json <run>/daylight_rules.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
