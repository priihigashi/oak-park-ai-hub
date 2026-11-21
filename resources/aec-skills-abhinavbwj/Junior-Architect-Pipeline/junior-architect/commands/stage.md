---
description: Run every junior task for one RIBA stage (0-7) in dependency order, one gated run at a time.
argument-hint: <stage 0-7>
---

Delegate to the **pipeline-orchestrator** agent.

Stage: $ARGUMENTS

1. Read `pipeline.json` and list every task whose `stages` include this stage, in dependency order:
   - brief-digest, site-dossier
   - code-research, planning-constraints
   - area-schedule, room-data-sheets
   - door-schedule, window-schedule, model-audit
   - drawing-qa, sheet-register
   - spec-section
   - rfi-response, submittal-review
   - meeting-minutes, site-visit-report
2. Show the junior the list with each task's ceiling and what they will be asked to predict. Let them drop or reorder tasks.
3. Run the tasks one at a time, following each task command's six steps. Open the next run only after the previous one has closed.
4. When the stage is done, summarise per task:
   - checker errors found;
   - the junior's findings;
   - what was escalated;
   - what is still open.

Then hand over to the **mentor** agent for the learning summary.
