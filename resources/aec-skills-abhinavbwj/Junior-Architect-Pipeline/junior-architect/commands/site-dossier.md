---
description: Brief and site: site dossier (RIBA stage 1; ceiling A2). A gated pipeline run with checker check_trace.
argument-hint: [autonomy A0-A2] [notes]
---

You are running the **site-dossier** task of the Junior Architect Pipeline. Engage the `brief-and-site` and `jap-core` skills, and delegate the work to the **brief-analyst** agent.

Arguments: $ARGUMENTS

1. **Open the run.** Run the pipeline CLI (its path is in this session's context): `start site-dossier <level>`. The level is the one in the arguments, or the ceiling A2, and never above it.
2. **Inputs.** Confirm you have site sources (survey, cadastre extract, planning portal pages) saved as text (site.txt). If anything is missing, ask the junior.
3. **The junior first.** Ask the junior to do this before you start: **Predict the two site constraints that will matter most, then check them against the dossier.** They record it themselves with `! <cli> predict "..."`. Hooks block model access (MCP tools) and the deliverable until they do. Never write it for them.
4. **The work.** The brief-analyst agent produces `.jap/runs/<run>/site_dossier.md`. Hosts: none (document task). Watch for: outdated data source; wrong parcel; unsourced figure.
5. **The check.** Run `check <run>/site_dossier.md site.txt` (`<run>` = `.jap/runs/<run id>`). Show the junior every error and warning as a redline (item, problem, fix). A failing check is reported as failing. Never present a number the checker has not confirmed.
6. **The review.** The junior accepts or rejects each item with a reason, adds `found: ...` for anything the checker missed, and records it with `! <cli> review "..."`. Then run `close`.

Escalate to a named senior anything touching code compliance, fire, structure, contract or cost.
