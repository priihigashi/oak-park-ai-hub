# Private Agent Rules Moved

This public repo no longer stores Priscila's private agent rulebook.

Canonical private source:

- Private repo: `priihigashi/priscila-workspace`
- Private file: `AGENTS.md`
- Migration checkpoint: private commit `ad9e011`

Do not add personal account details, private credentials routes, family information, private inbox information, finance notes, or assistant memory back to this public file.

Public `oak-park-ai-hub` should contain only automation/code and public-safe documentation.

## Public content guidance (business, non-private)
- **OPC content/design work: read `docs/OPC_DESIGN_SYSTEM.md` FIRST** — brand tokens, approved templates, folder routing, copy rules. Never improvise OPC design.
- Skills: `skills/shared/opc-carousel-creator/` (create posts) + `skills/shared/opc-carousel-reviewer/` (brand gate). Install: symlink from `~/.agents/skills/` into `~/.claude/skills/` and `~/.codex/skills/`.
- Claude agent definition: `claude-config/agents/opc-content-creator.md` → copy to `~/.claude/agents/`.
