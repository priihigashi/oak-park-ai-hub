# Focus Partner state moved to private repo

**Last updated: 2026-07-14 — privacy split.**

This public repo no longer stores Priscila's live Focus Partner state, journal memory, personal planning details, finance notes, family references, or private assistant memory.

Canonical private source now lives in:

- Private repo: `priihigashi/priscila-workspace`
- Private path: `.claude/focus-partner-state.md`
- Migration checkpoint: private commit `dd5ba9e` (`Move Focus Partner package into private workspace`)

Rules for assistants:

1. Do **not** add private Focus Partner state back to this public repo.
2. Read/update the private repo `priihigashi/priscila-workspace` instead.
3. Public `priihigashi/oak-park-ai-hub` is for automation/code that is safe to be public.
4. Keep the Google Sheet mirror aligned when practical, but private Markdown is the canonical Focus memory.

Remaining privacy work:

- Scrub old Git history from this public repo from the Mac/authorized git environment.
- Sanitize any public scripts/workflows that still contain hardcoded private emails or personal data.
- Reroute any automation that writes daily agent state into public paths.
