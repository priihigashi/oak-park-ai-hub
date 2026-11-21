---
description: Analysis, coordination and exchange: model audit (RIBA stage 3, 4, 5; ceiling A2). A gated pipeline run with checker check_schedule.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **model-audit** task of the Junior Architect Pipeline. Engage the `model-audit` and `jap-core` skills, and delegate the work to the **model-auditor** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start model-audit <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the model. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Predict the three worst model-health problems before the audit runs.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The model-auditor agent produces `.jap/runs/<run>/model_audit.csv`. Hosts: Revit, Rhino. Capabilities needed: read model warnings and health; read element statistics; list layers and document settings; purge unused (with the junior's go-ahead). Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: unplaced or unbounded rooms; elements on wrong level or layer; unit settings wrong; orphaned views and sheets.
5. **The check.** Run `check <run>/model_audit.csv <run>/model_audit.json audit` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
