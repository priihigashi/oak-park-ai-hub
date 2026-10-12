# HANDOFF 2026-10-12 — Reel "O presidente muda. A Câmara, não." (Colagem) + Kit Vox

## Pra colar no chat novo
"Leia o HANDOFF_2026-10-12_congresso_reel (Drive › Productivity & Routine, e no GitHub priihigashi/oak-park-ai-hub, branch feat/collage-reel-format, docs/templates/collage_reel/). Refaça o reel do Congresso com visual PREMIUM usando o Kit Vox e as referências — não o visual atual."

## Onde está tudo
- Código/template: GitHub `priihigashi/oak-park-ai-hub` › branch `feat/collage-reel-format` › `docs/templates/collage_reel/`
  - `congresso.html` (demo atual v7) · `kit_vox.html` + `fx2.js` (efeitos aprendidos dos tutoriais) · `engine.js`/`fx.js` (motor) · `capture.js` (render) · `audio.py` (sons)
  - Dados: `data/camara_ideologia_1995_2023.json` (bancadas eleitas 1994–2026 + classificação + FLAGS)
  - Regras: `MOVIMENTOS.md` (§2b cor, §2c alinhamento/camadas, §3b Kit Vox mov. 44–55), `INVESTIGACAO.md`, `REPERTORIO.md`, `CATALOGO_CENAS.csv`
- Referências baixadas (vídeo + folha de quadros + transcrição + áudio): Drive › News › Templates › Videos › colagem-reel-template › `_entrada_refs`
  - Baixar mais: adicionar linha `nome url` em `ref_urls.txt` e dar push na branch → workflow `ref_fetch.yml` sobe tudo pro Drive.

## Dados (verificados)
- Bancadas ELEITAS na Câmara (513) por espectro, régua Bolognesi, Ribeiro & Codato (2023). Bloco direita (dir.+centro-dir.) teve maioria em 9 de 9 Câmaras (1995–2027), média 71%.
- 2027 = Câmara eleita em 04/10/2026, contagem da Câmara/SGM com 99,99% apurado (CNN 05/10/2026). TSE ainda diplomando → conferir. Presidente: 2º turno 25/10/2026.
- Flags: anos 1994–2022 vieram das tabelas da Wikipedia que citam o TSE → conferir no TSE; federações 2022/2026 classificadas pelo partido dominante; PRD-Solidariedade = centro-direita (flag); Missão (1) sem classificação.

## Feedback da Priih sobre a v7 (fazer no chat novo)
1. **Visual pobre / brega no final.** Tela preta lisa = ruim. Faltam TEXTURAS e o estilo das referências (Vox: fundo em camadas com fotos do tema, P&B + tinta, parallax, colagem com pessoas reais recortadas, mistura P&B e cor). Usar o Kit Vox de verdade.
2. **Cena da coroa:** silhueta genérica + faixa "CÂMARA" entre cabeça e coroa ficou confusa. Refazer como colagem: político de terno (imagem de banco/IA, NÃO identificável) com maquiagem de palhaço recebendo a coroa, e o Congresso (foto do prédio, textura) barrando.
   - ⚠️ Não fazer parecido com candidato real (ela citou Flávio): estamos em 2º turno até 25/10/2026; a regra do TSE sobre IA (Res. 23.732/2024) proíbe deepfake de candidato e exige rótulo em conteúdo feito com IA. Personagem genérico + "imagem gerada por IA".
   - Precisão: leis, orçamento e derrubar veto = CONGRESSO (Câmara + Senado). Autorizar impeachment = Câmara. Escrever certo.
3. **Primeira frase de análise (embaixo):** na primeira vez que aparece, desfocar/escurecer o resto da tela por ~1s e destacar só a frase + uma seta ("essa frase muda a cada mandato"). Rápido, elegante, nada brego.
4. **Combinações de cor:** ela achou de mau gosto. Seguir as referências; revezar paletas (MOVIMENTOS §2b); evitar tela chapada sem textura.
5. **Medo dela:** "não quero que ninguém tire sarro de mim". Prioridade: acabamento premium e factual impecável.
6. **Glitch na transição entre cenas finais:** quando uma cena final sai (fade) e a próxima entra, o gráfico da corrida aparece por baixo por um instante (ex.: entre a vencedora e o fecho). Correção: depois de RACE_END esconder o gráfico (ou pôr fundo sólido/textura fixa por trás das cenas finais) e fazer crossfade cena→cena, nunca cena→vazio.
7. Mantém: gancho no início ("O presidente muda. A Câmara, não."), corrida de barras, ano contando no lugar, pausa+som por mandato, % em cinza, Bloco direita/esquerda coloridos, "pura", 2027 com nota, revelação final (vencedora) com celebração conceitual, pergunta final sobre voto pra deputado.

## Pendências fora do reel
- Upload da biblioteca completa (demos/ref 00–05/75 cenas) do Mac pro Drive: token OAuth não está em ~/ClaudeWorkspace/Credentials; alternativa = workflow do GitHub com secret SHEETS_TOKEN.
- Refs 06–08 (telas em 3) falharam no download. Refs 09–11, 15–17 baixadas, falta analisar (ver folhas de quadros na pasta _entrada_refs).
- Skill: botão de salvar não funciona pra skill sincronizada; propor como skill nova ou recriar.
