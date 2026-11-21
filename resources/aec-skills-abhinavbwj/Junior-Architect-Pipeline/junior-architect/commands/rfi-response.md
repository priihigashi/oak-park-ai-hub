---
description: Specification and construction administration: rfi response (RIBA stage 5; ceiling A1). A gated pipeline run with checker check_refs.
argument-hint: [autonomy A0-A1] [notes]
---

You are running the **rfi-response** task of the Junior Architect Pipeline. Engage the `construction-admin` and `jap-core` skills, and delegate the work to the **document-controller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start rfi-response <level>`. The level is the one in the arguments, or the ceiling A1, and never above it.
2. **Inputs.** Confirm you have the RFI text and the current sheet register (sheets.csv). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Write the intent of the answer in one sentence before the agent words it.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The document-controller agent produces `.jap/runs/<run>/rfi_response.md`. Hosts: Revit. Capabilities needed: find elements and capture views. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: answer changes scope without saying so; reference to a superseded drawing; contractual commitment the architect cannot give.
5. **The check.** Run `check <run>/rfi_response.md sheets.csv` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
