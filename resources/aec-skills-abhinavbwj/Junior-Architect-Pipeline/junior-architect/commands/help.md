---
description: What the Junior Architect Pipeline does, every task it runs, and how to start.
---

Explain the Junior Architect Pipeline to the user in plain language, then show the task map.

1. **What it is.** A gated pipeline for junior-architect production work. Claude does the retrieval, drafting and counting through specialist agents and MCP connections to Rhino, Grasshopper, Revit and Blender. The junior keeps every judgement step: they predict before the run, review the redline, and explain deviations. Deterministic checkers recompute every number, and hooks enforce the gates.
2. **The run cycle.** `start`, then the junior's prediction (at A1 and A2), then the agent's work, then the checker's report, then the junior's review, then `close`, which writes to the learning log.
3. **Autonomy levels A0 to A4**, from `pipeline.json`. Each task has a ceiling. Code, specification and contract tasks stay at A1.
4. **The task map.** Run the pipeline CLI's `tasks` and show its output grouped by family (BRIEF-SITE, REGULATION, MODELLING, DRAFTING, SCHEDULES, VISUAL, COORDINATION, ADMIN), as a table: task, stages, ceiling, checker, agent.
5. **Commands:**
   - `/junior-architect:setup`: create `.jap/` and fill in the project standards
   - `/junior-architect:stage <n>`: run every task for a RIBA stage in order
   - one command per task: `/junior-architect:area-schedule`, `/junior-architect:door-schedule`, `/junior-architect:code-research`, and the others
   - `/junior-architect:status`: show the open run
   - `/junior-architect:learn`: the learning log and what to practise next
6. **The gates.** Claude cannot write the junior's prediction or review, cannot forge a checker report, cannot touch the model before a prediction at A1 and A2, and cannot finish a task whose deliverable has no checker report.
7. **Hosts.** Rhino, Grasshopper, Revit and Blender are reached through whichever MCP servers the user has connected. Each task lists the capabilities it needs, and without a server the pipeline works from exported files; see `mcp/README.md`. Run `node tests/examples.test.js` to confirm all 20 checkers on the seeded faults.

Close with one line: run `/junior-architect:setup` in the project folder to begin.
