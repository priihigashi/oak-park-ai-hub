---
description: Schedules and quantities: window schedule (RIBA stage 4; ceiling A3). A gated pipeline run with checker check_schedule.
argument-hint: [autonomy A0-A3] [notes]
---

You are running the **window-schedule** task of the Junior Architect Pipeline. Engage the `schedules` and `jap-core` skills, and delegate the work to the **quantity-scheduler** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start window-schedule <level>`. The level is the one in the arguments, or the ceiling A3, and never above it.
2. **Inputs.** Confirm you have the model and the office window standard (required_fields.windows). If anything is missing, ask the junior.
3. **The junior first.** At A3 no prediction is required. If the junior runs it at A1 or A2, ask them: **Check the three windows that carry the most risk (largest, highest, fire or acoustic) by hand.**
4. **The work.** The quantity-scheduler agent produces `.jap/runs/<run>/window_schedule.csv`. Hosts: Revit. Capabilities needed: read windows and their parameters; renumber marks; read schedule data. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: count mismatch; U-value or g-value missing; opening size from the wrong reference.
5. **The check.** Run `check <run>/window_schedule.csv <run>/model_windows.json windows` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
