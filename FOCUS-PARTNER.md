# Focus Partner — Priscila's portable ADHD focus system

**Last updated: 2026-07-13** — this repo is the source of truth. Includes: `/focus` shortcut, full backlog with sub-steps, Monday patterns, Finance/Investments detail, and a guided **Manifestation Module** (10-min morning practice).

This is a complete, portable "focus partner" that **any AI assistant** can run — Claude Code, Codex, or anything else that can read files from GitHub. If Priscila says *"go to GitHub and read the focus MD and help me,"* **this is that MD.**

## When Priscila says "update"
Re-read the files in this repo, compare the **Last updated: YYYY-MM-DD** line at the top of `.claude/agents/focus-partner.md` and `.claude/focus-partner-state.md` against the local copies in `~/.claude/`, and if the repo is newer, copy the newer versions into `~/.claude/`. Then tell her the date you pulled. The repo always wins.

---

## If you are an AI assistant: how to be her focus partner
1. Read **`.claude/agents/focus-partner.md`** — the full brain: who she is, how to work with her, her planning frame (Rule of 3 + Eisenhower matrix), the Manifestation Module, and her known patterns/traps. Follow it exactly.
2. Read **`.claude/focus-partner-state.md`** — the live state: her master backlog, this week's plan, pending tasks, session log, manifestation log, and behavioral patterns. This is what's currently true.
3. Then act as the brain describes: (mornings) run the Manifestation Module first, give her the report, run the planning frame, hand her **ONE thing at a time**, keep replies short. When anything changes, **update the state file and commit it back here** so the next computer stays in sync.

---

## The files (the whole package)
| File | What it is |
|---|---|
| `.claude/agents/focus-partner.md` | The **brain** — how to help her (rules, planning frame, manifestation module, her patterns) |
| `.claude/focus-partner-state.md` | The **live state** — backlog, weekly plan, pending, manifestation log, patterns |
| `.claude/commands/focus.md` | Claude Code shortcut `/focus` — starts a session |
| `.claude/commands/exit.md` + `handoff.md` | Claude Code shortcuts `/exit` `/handoff` — write handoff + save state |

---

## Install on a new computer (Claude Code)
Pull this repo and copy into your `~/.claude/`, same relative paths:
- `.claude/agents/focus-partner.md` → `~/.claude/agents/focus-partner.md`
- `.claude/focus-partner-state.md` → `~/.claude/focus-partner-state.md`
- `.claude/commands/focus.md` `exit.md` `handoff.md` → `~/.claude/commands/`

Then type `/focus` to start a session. `/exit` saves + pushes at the end.

---

## Using it in Codex (or any tool WITHOUT "skills")
Codex has no skills/agents, but it can read this repo. Just tell it:

> "Read `.claude/agents/focus-partner.md` and `.claude/focus-partner-state.md` in `priihigashi/oak-park-ai-hub`, then act as my focus partner per those files, and update the state file when we're done."

That's the whole thing — the brain + state are plain Markdown, **not Claude-specific**. Nothing here depends on Claude Code features.

---

## The one rule that keeps it working
Whoever helps her must **save changes back to `.claude/focus-partner-state.md` and commit it to this repo** at the end of a session (Claude Code does it with `/exit`). Everything important lives in these files — **never only in a chat.** If it's not in the state file + committed, the next computer won't know it.
