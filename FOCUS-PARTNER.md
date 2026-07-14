# Focus Partner moved to private workspace

**Last updated: 2026-07-14 — privacy split.**

The Focus Partner system contains personal planning, family, finance, journal, and assistant-memory details, so it no longer belongs in this public repo.

Canonical private source now lives in:

- Private repo: `priihigashi/priscila-workspace`
- Setup file: `FOCUS-PARTNER.md`
- Agent brain: `.claude/agents/focus-partner.md`
- Live state: `.claude/focus-partner-state.md`
- Commands: `.claude/commands/`
- Migration checkpoint: private commit `dd5ba9e` (`Move Focus Partner package into private workspace`)

## For Claude/Codex

Do not add private Focus Partner state back to `priihigashi/oak-park-ai-hub`.

Use this prompt instead:

> Read `FOCUS-PARTNER.md`, `.claude/agents/focus-partner.md`, and `.claude/focus-partner-state.md` in private repo `priihigashi/priscila-workspace`, then act as Priscila's Focus Partner per those files. Keep the Google Sheet mirror aligned when practical, and update the private GitHub state file when done.

## What stays public here

`priihigashi/oak-park-ai-hub` should contain only automation/code and public-safe docs. Any private memory, journal state, finance details, family notes, or personal assistant instructions belong in `priihigashi/priscila-workspace`.

## Remaining privacy work

- Scrub old Git history from this public repo.
- Sanitize public scripts/workflows that still contain hardcoded private emails or personal data.
- Reroute automations that write daily agent state into public paths.
