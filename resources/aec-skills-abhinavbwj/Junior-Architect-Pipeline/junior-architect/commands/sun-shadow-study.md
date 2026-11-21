---
description: Visualisation and presentation: sun shadow study (RIBA stage 2, 3; ceiling A2). A gated pipeline run with checker check_render.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **sun-shadow-study** task of the Junior Architect Pipeline. Engage the `visualisation` and `jap-core` skills, and delegate the work to the **visualiser** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start sun-shadow-study <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have the site latitude, longitude and time zone, and the dates and times required (equinox and solstices are typical). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Predict which spaces are in shade at 15:00 on the winter solstice before the study runs.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The visualiser agent produces `.jap/runs/<run>/renders.json`. Hosts: Revit, Rhino, Blender. Capabilities needed: set the sun from location, date and time; run a sun study; capture each step; render stills. Use the MCP server the user has connected for each host (`mcp__<server>__<tool>`). If it is not connected, or lacks a capability, say so and work from files the junior exports. Watch for: sun not set to the real site and date; daylight saving time ignored; north misaligned; neighbouring buildings missing.
5. **The check.** Run `check <run>/renders.json` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
