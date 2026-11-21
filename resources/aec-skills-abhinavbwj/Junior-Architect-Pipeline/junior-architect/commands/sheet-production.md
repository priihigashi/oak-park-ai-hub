---
description: Drafting and documentation: sheet production (RIBA stage 3, 4, 5; ceiling A2). A gated pipeline run with checker check_sheets.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **sheet-production** task of the Junior Architect Pipeline. Engage the `drawings-and-sheets` and `jap-core` skills, and delegate the work to the **documentation-lead** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start sheet-production <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the drawing list, the title block, the naming convention and status codes in project.json. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Lay out one sheet by hand: what goes where so the drawing reads in order.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The documentation-lead agent produces `.jap/runs/<run>/sheets.csv`. Hosts: Revit. Capabilities needed: create sheets and place views; fill title block fields; create revisions and revision clouds; build sheet sets and export PDF; list sheets. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: views placed at the wrong scale; title block fields empty; revision not recorded; names off the convention.
5. **The check.** Run `check <run>/sheets.csv` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
