---
description: 3D modelling, BIM and Grasshopper: grasshopper definition (RIBA stage 2, 3, 4; ceiling A2). A gated pipeline run with checker check_gh.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **grasshopper-definition** task of the Junior Architect Pipeline. Engage the `grasshopper` and `jap-core` skills, and delegate the work to the **grasshopper-builder** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start grasshopper-definition <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the design rule in words and the inputs it reads from the Rhino model. If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Draw the dataflow (inputs, operations, outputs) on paper before the definition is built.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The grasshopper-builder agent produces `.jap/runs/<run>/gh_export.json`. Hosts: Grasshopper, Rhino. Capabilities needed: create or open a definition; add and wire components; set slider values; solve and read each component's runtime state; bake to named layers; save the definition. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: components in error or warning; required inputs left unconnected; unnamed sliders; internalised geometry that stops following the model; data trees grafted or flattened by accident.
5. **The check.** Run `check <run>/gh_export.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
