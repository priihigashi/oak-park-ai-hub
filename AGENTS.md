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

## OPC content — Codex behavior rules (mirrors opc-content-creator agent)

When asked to create ANY Oak Park Construction post, carousel, before-after, or graphic:

**Load in this order before any design work:**
1. `docs/OPC_DESIGN_SYSTEM.md` — tokens, fonts, layout rules, template list, folder routing
2. `scripts/content_creator/opc_template_catalog.json` — pick template by purpose/good_for
3. CONTENT_FORMATS Drive doc `1XqXSyJC_iHMTrmMxpM5ZR7S-WQxz19HhDJO1HomdncM` — check registered FORMAT
4. Target Drive folder for prior version numbering (`vN_proof-<slug>` convention)

**Then follow `skills/shared/opc-carousel-creator/SKILL.md` exactly.**

**Hard refusals — never do these:**
- Use any color/font outside the OPC token set (`#0A0A0A`, `#CBCC10`, `#F0EBE3`, `#7A7267` + template-derived shades). If unsure — stop, re-read the design system, never improvise.
- AI text-to-image generation for layouts (Ideogram, DALL-E, Canva AI, etc. hallucinate the brand).
- Publish, schedule, or post anywhere without Priscila's explicit per-version approval.
- Fabricate names, addresses, dates, stats, crew, or project IDs to fill template fields.
- Deliver a single design version — always deliver 3 variants (template's v1 dark / v2 cream / v3 lime-on-dark).

**Storage:** Marketing SHARED Drive (`driveId 0AIPzwsJD_qqzUk9PVA`) → Content (`1lyWGwQiUPAVoMzb8vfQ0fBw72M1A2UfR`). Never My Drive. Always `supportsAllDrives=true`.

**Run `skills/shared/opc-carousel-reviewer/SKILL.md` as a gate before anything reaches Priscila.** Any FAIL = fix before showing her.
