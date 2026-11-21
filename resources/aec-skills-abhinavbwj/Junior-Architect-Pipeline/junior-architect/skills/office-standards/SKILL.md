---
name: office-standards
description: Encoding an office's standards for the pipeline. Covers .jap/project.json, CLAUDE.md and hooks, what belongs where, and how to keep standards in version control. Use for setup and whenever office standards change.
---

# Office standards

## Three places, three jobs

| Place | What goes there | How Claude treats it |
|---|---|---|
| `.jap/project.json` | Machine-readable project standards: units, area standard and definition, tolerances, layers, code editions, naming pattern, status codes, required fields, escalation rule | Every checker reads it, so it decides pass or fail |
| `CLAUDE.md` (project root) | The office's way of working in words: drawing conventions, tone of correspondence, who to escalate to, naming of files | Loaded every session as context. It is guidance, and the model can still deviate. |
| Hooks (this plugin's `hooks/hooks.json`) | The rules that must hold whatever the model decides | Enforced on every tool call and at every stop |

## Put a rule where it can actually hold
- A rule that must never be broken (who writes the prediction, who writes the report) is a hook.
- A rule that decides pass or fail is in `project.json` and a checker.
- A preference is in `CLAUDE.md`.

## Version control
Keep `CLAUDE.md`, `.jap/project.json` and any office edits to `pipeline.json` in the project repository. Review changes to them as you would review a change to the office manual. Keep `.jap/runs/` too: it is the record of who checked what against which rule.
