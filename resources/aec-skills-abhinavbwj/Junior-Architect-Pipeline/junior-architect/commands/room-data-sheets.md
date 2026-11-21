---
description: Schedules and quantities: room data sheets (RIBA stage 3, 4; ceiling A2). A gated pipeline run with checker check_schedule.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **room-data-sheets** task of the Junior Architect Pipeline. Engage the `schedules` and `jap-core` skills, and delegate the work to the **quantity-scheduler** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start room-data-sheets <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the model and the office room data sheet fields (required_fields.rooms). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Fill one room data sheet by hand per room type, then compare with the agent's.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The quantity-scheduler agent produces `.jap/runs/<run>/room_data_sheets.csv`. Hosts: Revit. Capabilities needed: read rooms and their parameters; set parameters; read schedule data. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: missing required field; finishes inconsistent with the room type; stale model state.
5. **The check.** Run `check <run>/room_data_sheets.csv <run>/model_rooms.json rooms` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
