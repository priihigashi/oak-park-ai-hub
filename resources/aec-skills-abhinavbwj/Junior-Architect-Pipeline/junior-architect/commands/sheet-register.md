---
description: Drafting and documentation: sheet register (RIBA stage 4, 5; ceiling A3). A gated pipeline run with checker check_sheets.
argument-hint: [autonomy A0-A3] [notes]
---

You are running the **sheet-register** task of the Junior Architect Pipeline. Engage the `records-and-correspondence` and `jap-core` skills, and delegate the work to the **document-controller** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start sheet-register <level>`. The level is the one in the arguments, or the ceiling A3, and never above it.
2. **Inputs.** Confirm you have the sheet list export from the model (sheets.csv). If anything is missing, ask the junior.
3. **The junior first.** At A3 no prediction is required. If the junior runs it at A1 or A2, ask them: **Confirm the revision and status codes of every sheet issued for construction.**
4. **The work.** The document-controller agent produces `.jap/runs/<run>/sheet_register.csv`. Hosts: Revit. Capabilities needed: list sheets and revisions. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: revision not incremented; status code wrong for the purpose; name not compliant with the naming convention.
5. **The check.** Run `check <run>/sheet_register.csv` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
