# Private Claude Rules Moved

This public repo no longer stores Priscila's private Claude/Codex rulebook.

Canonical private source:

- Private repo: `priihigashi/priscila-workspace`
- Private file: `CLAUDE.md`
- Migration checkpoint: private commit `ad9e011`

Do not add personal account details, private credentials routes, family information, private inbox information, finance notes, or assistant memory back to this public file.

Public `oak-park-ai-hub` should contain only automation/code and public-safe documentation.

## Public content guidance (business, non-private)
- **OPC content/design work: read `docs/OPC_DESIGN_SYSTEM.md` FIRST** — brand tokens, approved templates, folder routing, copy rules. Never improvise OPC design.
- Skills: `skills/shared/opc-carousel-creator/` (create posts) + `skills/shared/opc-carousel-reviewer/` (brand gate). Install: symlink from `~/.agents/skills/` into `~/.claude/skills/` and `~/.codex/skills/`.
- Claude agent definition: `claude-config/agents/opc-content-creator.md` → copy to `~/.claude/agents/`.


## Quando um conector cair

### REGRA 1, três cópias por 24 horas
Toda mídia de trabalho de um conteúdo em andamento (MP4 renderizado, mp3 das vozes, HTML/fonte da prévia) é salva em 3 lugares: Google Drive (pasta do conteúdo), GitHub (repo priihigashi/oak-park-ai-hub, pasta temporária) e meu computador. Assim, se um conector cair, os outros seguram. Depois de ~24 horas, apague as cópias extras do GitHub e do computador e deixe só a do Google Drive.

### REGRA 2, rotas reserva quando um conector cair
Nunca pare o trabalho porque um conector caiu. Avance o máximo possível (troque telas e textos, faça voz provisória grátis com as falas novas) e já me ofereça uma rota reserva pronta: um prompt pra eu colar em outro Claude que busque o arquivo (Drive, Composio, meu computador ou GitHub) e me devolva o texto inteiro, palavra por palavra, pra eu trazer de volta. Antes de dizer que algo travou, confira status.claude.com.
