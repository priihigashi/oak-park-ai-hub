---
description: Specification and construction administration: spec section (RIBA stage 4; ceiling A1). A gated pipeline run with checker check_spec.
argument-hint: [autonomy A0-A1] [notes]
---

You are running the **spec-section** task of the Junior Architect Pipeline. Engage the `specifications` and `jap-core` skills, and delegate the work to the **spec-writer** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start spec-section <level>`. The level is the one in the arguments, or the ceiling A1, and never above it.
2. **Inputs.** Confirm you have the section to write, the standards register (standards_register.csv) and the related schedule. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Write the performance clause by hand once per section type before the agent drafts the rest.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The spec-writer agent produces `.jap/runs/<run>/spec_section.md`. Hosts: Revit. Capabilities needed: read types and material information. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: wrong or withdrawn standard reference; product line with no schedule item; prescriptive and performance clauses in conflict.
5. **The check.** Run `check <run>/spec_section.md standards_register.csv <schedule>.csv` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
