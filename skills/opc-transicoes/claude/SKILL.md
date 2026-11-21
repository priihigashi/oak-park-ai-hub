---
name: opc-transicoes
description: OPC (Oak Park Construction) reels de transição antes → depois no estilo dos reels do @abhinavbwj (manchas de cor, rabisco, planta, desenho, gente entrando, régua, ideias A/B/C). Use quando a Priih pedir transição, antes e depois animado, "o que dá pra fazer nesse espaço" ou mandar reel dele.
---

> Esta skill existe em 3 lugares (Mac, Drive "Skills de Reels e Carrosséis > opc-transicoes > Claude/ChatGPT/Improved", GitHub oak-park-ai-hub skills/opc-transicoes/claude/). Mudou aqui, muda nos 3 e anota no Skills Tracker.

# OPC · Transições antes → depois

## Onde está tudo
- Templates prontos (site): painel-da-manha.vercel.app/templates/ → grupo OPC, cards 163 a 166. Código: repo priihigashi/painel-da-manha, `templates/opc-transicoes/` (branch claude/opc-transicoes-20261121, PR #14).
  - `_motor.js` + `_motor.css`: motor comum. Cada template define `window.CENA={dur,codigo,titulo,inicia(),desenha(t)}`; tudo é função de t. Controles: play, arrastar, −5/+5/+10/+30 s, velocidades 1/1,05/1,1/1,2/1,5/2/3x, som, notas com copiar, baixar HTML. `?editar=1` troca foto (clique) e texto (data-ed). `?cap=1` + `window.__ir(t)` grava quadro a quadro (Playwright → ffmpeg).
  - `claude/01` Sketch reveal · `02` Folha/chuva cai + desenho da obra + gente entrando (`?clima=folhas|chuva|nada`) · `03` Faixas de cor + régua antes/depois · `04` Um espaço, 3 ideias A/B/C.
  - `chatgpt/` = versão GPT (LEIA-ME com o formato). `referencias/README.md` = os 8 reels analisados.
- Drive: Marketing › Content Reels & TikTok › "OPC · Transições antes-depois (ref. abhinavbwj)" (1rvzAtIEkntOTDVtSiwsxQKBaNArWlmw_) com resources (vídeos de referência, transcrição, quadros), Claude (prévias), GPT (do ChatGPT).
- Plugins grátis do Abhinav (MIT) copiados em oak-park-ai-hub `resources/aec-skills-abhinavbwj/`: Skills-Architects (29 skills + norma EUA), urban-design-skills-claude, Claude-skills-for-Computational-Designers, Junior-Architect-Pipeline. Use pra checar números e termos técnicos de verdade (códigos, áreas, ventilação, luz) antes de pôr na tela.

## Passo a passo
1. Baixar o reel de referência com a skill baixar-reel-instagram (GitHub Actions; transcrição + quadros + BPM com librosa).
2. Escolher um PROJETO DIFERENTE pra cada template (Drive OPC: pastas `<projeto>__<tipo>__BEFORE/DURING/AFTER__...`). Projetos já usados: Kinney (01), Pergola outdoor living (02), Harbor Court (03), Dockside (04).
3. Antes e depois no MESMO ângulo. Alinhar com OpenCV (pontos que batem → estimateAffinePartial2D / similaridade; conferir com mistura 50%). Se o ângulo for diferente demais, gerar com IA (ChatGPT imagem) a foto que falta a partir da boa, sem mexer na câmera. O meio pode ser desenho: linhas do depois (Canny) ou render (cv2.stylization).
4. Cortar 9:16 (1080×1920), copiar a pasta de um template, trocar `antes.jpg`/`depois.jpg`, refazer `linhas.png`/`render.jpg`, ajustar polígonos das manchas na foto nova (grade de coordenadas ajuda).
5. Conferir quadros com Playwright (`?cap=1`), gerar miniatura + MP4 curto, cadastrar card (catalogo.json grupo O + fichas.json com prompt_para_chat), rodar `python3 scripts/templates-refeitos.py`, publicar (deploy Vercel só com o que mudou).
6. No fim: prompt pro ChatGPT fazer a versão dele em `chatgpt/` com os links.

## Regras
- Público: dono de casa nos EUA, texto em inglês, títulos discretos, área segura x 108–972, etiqueta em y 250, marca a 260 px do fundo (sobe se tiver gente embaixo).
- Nunca inventar etapa que a obra não teve; legenda do "plano" só com o que se vê no depois.
- Sugestões (A/B/C, "o que dá pra fazer aqui": pérgola, addition, fogueira, horta, playground, layouts de cozinha) levam aviso "Concept ideas only. Final layout by a licensed designer." A OPC constrói; design é com designer.
- Música: o som do reel de referência na prévia é só ritmo. Conta comercial usa áudio da biblioteca comercial do Instagram; escolher o som em alta lá dentro na hora de postar.
- Gente: bonequinhos chapados (flat) ou silhuetas brancas, feitos em SVG por código.
