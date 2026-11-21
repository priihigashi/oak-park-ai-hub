---
description: Drafting and documentation: drawing qa (RIBA stage 3, 4, 5; ceiling A2). A gated pipeline run with checker check_sheets.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **drawing-qa** task of the Junior Architect Pipeline. Engage the `drawing-qa` and `jap-core` skills, and delegate the work to the **drawing-checker** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start drawing-qa <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the sheet list export (sheets.csv) and the PDFs or the model. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Accept or reject each redline item with a one-line reason; flag items the checker cannot see.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The drawing-checker agent produces `.jap/runs/<run>/redline.csv`. Hosts: Revit. Capabilities needed: list sheets and their views; capture views; export PDF. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: confident false positive; missed coordination clash; title block field wrong; reference to a non-existent sheet.
5. **The check.** Run `check sheets.csv` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
