# Focus Partner — Priscila's portable ADHD focus system

**Last updated: 2026-07-14 (rev7 setup note)** — this repo is the source of truth. Includes: `/focus` shortcut, full backlog with sub-steps, Monday patterns, Finance/Investments detail, guided **Manifestation Module**, Google Sheet mirror, Library Index, Morning Command Center launchers, **Boletim Diario**, and the future guided app-window idea.

This is a complete, portable "focus partner" that **any AI assistant** can run — Claude Code, Codex, or anything else that can read files from GitHub. If Priscila says *"go to GitHub and read the focus MD and help me,"* **this is that MD.**

## When Priscila says "update"
Re-read the files in this repo, compare the **Last updated: YYYY-MM-DD (revN)** line at the top of `.claude/agents/focus-partner.md` and `.claude/focus-partner-state.md` against the local copies in `~/.claude/`, and if the repo is newer, copy the newer versions into `~/.claude/`. Then tell her the date + rev you pulled. The repo always wins.

Important coordination rule: Claude and Codex may both edit this repo. Before writing, fetch the newest GitHub copy of the file you are about to update and merge your note into that copy. Never overwrite a newer rev with a stale full-file copy.

---

## If you are an AI assistant: how to be her focus partner
1. Read **`.claude/agents/focus-partner.md`** — the full brain: who she is, how to work with her, her planning frame (Rule of 3 + Eisenhower matrix), the Manifestation Module, and her known patterns/traps. Follow it exactly.
2. Read **`.claude/focus-partner-state.md`** — the live state: her master backlog, this week's plan, pending tasks, session log, manifestation log, and behavioral patterns. This is what's currently true.
3. Then act as the brain describes: (mornings) run the Manifestation Module first, give her the report, run the planning frame, hand her **ONE thing at a time**, keep replies short. When anything changes, **update the state file and commit it back here** so the next computer stays in sync.
4. A lightweight Google Sheet mirror exists for human scanning: `_Focus Partner — STATE` in Drive folder `Productivity & Routine / Focus Partner`. The GitHub Markdown state is still canonical; the Sheet is a mirror, not the source of truth. Keep both aligned when practical.
5. Use the `Library Index` in the Sheet/state before searching randomly. Every master plan, dashboard, Drive folder, website, stock/finance tracker, and important handoff should be listed there.

---

## Current Focus System Pieces
- **Canonical Markdown:** `.claude/focus-partner-state.md` in this repo.
- **Human-readable Sheet mirror:** `_Focus Partner — STATE` at `https://docs.google.com/spreadsheets/d/1AlvtSGIZUWE1pzld2A8LL5bK4g9nRR4a4jqsOcfnY4c`.
- **Library Index:** tab inside the Focus Partner Sheet, mirrored in the state file.
- **Daily journal folder:** `Daily Journal — DROP HERE`, id `1eknXv30UHtuDVDDRJpyt3eBLqsxhjABB`.
- **Morning Command Center launchers:** see `scripts/MORNING-COMMAND-CENTER.md`, `scripts/focus-morning.bat`, and `scripts/focus-morning.command`.
- **Boletim Diario:** daily briefing link is part of the Morning Command Center and should not be treated as missing or separate. Current link: `https://priihigashi.github.io/ClaudeGallery/boletim-diario.html`.

## Important Pending Idea — Guided Command Center App
Priscila does **not** only want reminders. She is imagining a small app-like window/dashboard that opens and guides her through the morning instead of relying on memory. Capture this as a pending build idea in both the Sheet and Markdown state:

- Focus Partner / manifestation
- Today's 3
- Daily journal
- Boletim Diario
- finance/stocks/subscriptions check
- next calm action
- later: analysis/evaluation using real data and possibly Claude/OpenAI APIs

For now, the implemented system is launchers + calendar/reminder layers + links. The future version should feel like a guided journey, not just a popup. For finance/stocks, keep advice safe: inventory, visibility, alerts, rules, and education first; do not push buy/sell decisions as financial advice.

---

## The files (the whole package)
| File | What it is |
|---|---|
| `.claude/agents/focus-partner.md` | The **brain** — how to help her (rules, planning frame, manifestation module, her patterns) |
| `.claude/focus-partner-state.md` | The **live state** — backlog, weekly plan, pending, manifestation log, patterns |
| `.claude/commands/focus.md` | Claude Code shortcut `/focus` — starts a session |
| `.claude/commands/exit.md` + `handoff.md` | Claude Code shortcuts `/exit` `/handoff` — write handoff + save state |
| `scripts/MORNING-COMMAND-CENTER.md` | Setup instructions for morning launcher on Windows/Mac/iPhone |
| `scripts/focus-morning.bat` | Windows morning launcher |
| `scripts/focus-morning.command` | Mac morning launcher |

---

## Install on a new computer (Claude Code / Claude in VS Code)
Pull this repo and copy into your `~/.claude/`, same relative paths:
- `.claude/agents/focus-partner.md` → `~/.claude/agents/focus-partner.md`
- `.claude/focus-partner-state.md` → `~/.claude/focus-partner-state.md`
- `.claude/commands/focus.md` `exit.md` `handoff.md` → `~/.claude/commands/`

Then type `/focus` to start a session. `/exit` saves + pushes at the end.

---

## Using it in Codex (or any tool WITHOUT "skills")
Codex has no Claude Code skills/agents, but it can read this repo. Just tell it:

> "Read `FOCUS-PARTNER.md`, `.claude/agents/focus-partner.md`, and `.claude/focus-partner-state.md` in `priihigashi/oak-park-ai-hub`, then act as my focus partner per those files. Keep the Google Sheet mirror aligned when practical, and update the GitHub state file when we're done."

That's the whole thing — the brain + state are plain Markdown, **not Claude-specific**. Nothing here depends on Claude Code features except the `/focus`, `/exit`, and `/handoff` shortcuts.

---

## Prompt To Give Claude If Boletim Or The App Window Seems Missing
Use this when Claude says it cannot find Boletim, the launcher, or the command-center idea:

> Read the newest GitHub files in `priihigashi/oak-park-ai-hub`: `FOCUS-PARTNER.md`, `.claude/agents/focus-partner.md`, `.claude/focus-partner-state.md`, and `scripts/MORNING-COMMAND-CENTER.md`. Boletim Diario is part of the Morning Command Center, not a separate missing project. The future pending build is a guided app-like Command Center window that walks Priscila through manifestation, Today's 3, journal, Boletim, finance/stocks/subscriptions, and one calm next action. If you update anything, update `.claude/focus-partner-state.md` and keep the Google Sheet mirror `_Focus Partner — STATE` aligned when practical. Do not overwrite a newer rev.

---

## The one rule that keeps it working
Whoever helps her must **save changes back to `.claude/focus-partner-state.md` and commit it to this repo** at the end of a session (Claude Code does it with `/exit`). Everything important lives in these files — **never only in a chat.** If it's not in the state file + committed, the next computer won't know it.
