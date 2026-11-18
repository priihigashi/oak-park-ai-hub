# Skills de Reels e Carrosséis

## Regra dos 3 lugares
Todo skill de Reels/Carrosséis existe em 3 lugares, sempre iguais:

| Lugar | Caminho |
|---|---|
| Mac | `~/ClaudeWorkspace/skills/<skill>/<versão>/` |
| Google Drive | Tools, Skills & Flows > Skills > Skills de Reels e Carrosséis > `<Skill>` > `<Versão>` |
| GitHub | `priihigashi/oak-park-ai-hub/skills/<skill>/<versão>/` |

**Toda alteração deve ser feita nos 3.** Depois de mudar, adicione uma linha NOVA na planilha **Skills Tracker** (pasta Skills de Reels e Carrosséis). Nunca sobrescreva linha antiga.

Cada SKILL.md tem, logo abaixo do cabeçalho (frontmatter), o aviso "ESTE SKILL EXISTE EM 3 LUGARES" com os 3 caminhos.

## Estrutura de cada skill
```
<skill>/
├── Claude/     ← versão que o Claude usa (SKILL.md + scripts + templates)
├── ChatGPT/    ← versão adaptada pro ChatGPT/Codex
└── Improved/   ← versão melhorada em teste, antes de virar a oficial
```
No GitHub e no Mac as pastas ficam em minúsculas (`claude/`, `chatgpt/`, `improved/`).

## Skills espelhados
- Colonization BR (`colonization-br`, nome interno `coolonizacao-br`)

## Atualizar o Drive a partir do GitHub
Qualquer push em `skills/colonization-br/**` roda o workflow `skills_sync_drive.yml`, que copia a pasta pro Drive (OAuth, supportsAllDrives=True) e grava o resultado em `skills/_sync_report.json`.
