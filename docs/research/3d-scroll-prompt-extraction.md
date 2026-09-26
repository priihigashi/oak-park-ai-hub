# 3D Scroll Master Prompt — Extraction Note

Filed: 2026-09-26 by Daily Advancer
Source: Link 4 from 2026-09-21 saved resources task (Productivity & Routine doc)
Original doc: https://docs.google.com/document/d/1OeRStoCSHNC401-JdwfxoUPtuGJpRX2-AGxFRwseQfc/edit

---

## What This Is

A master prompt template for converting a reference video (YouTube or other) into an **interactive 3D scroll experience rendered in the browser**.

Created by: **Leandro Rezende**, UX Master — Nielsen Norman Group (NN/g)
LinkedIn: https://www.linkedin.com/in/lbrezende/
Instagram: https://www.instagram.com/uxunicornio
Design hub: https://www.instagram.com/designboosthub

Tech stack: **Three.js** (3D rendering), optional **Blender** (model production), reuses existing project components (e.g., React Flow cards/nodes for funnel apps).

---

## How It Works

You provide three inputs:
1. A reference video URL — the motion/composition you want to recreate
2. Your project's repository — so AI can reuse existing components
3. A style/interaction description — the desired look and feel

The AI analyzes the video for camera movement, transitions, and animation sequences, then recreates those scenes as real-time 3D objects in the browser.

---

## The Full Prompt (PT-BR, as written)

```
Transforme os vídeos de referência em uma experiência 3D interativa, renderizada diretamente no navegador.

Referências:
  - Vídeo(s) ou página com os vídeos: [INSIRA AQUI]
  - Repositório do meu projeto: [INSIRA AQUI]
  - Como quero que o resultado fique: [DESCREVA O ESTILO, OS ELEMENTOS E AS INTERAÇÕES]

Analise os vídeos para entender o roteiro, a composição visual, os movimentos de câmera, as transições e a sequência das animações.

Explore o repositório para identificar componentes, estilos e elementos do produto que possam ser reaproveitados. Preserve a identidade visual e os detalhes que tornam a interface reconhecível.

Recrie os elementos dos vídeos como objetos, cenas e animações 3D usando Three.js e, quando necessário, modelos produzidos no Blender. O resultado deve acontecer em tempo real no navegador, com profundidade, iluminação, materiais e movimentos de câmera bem trabalhados.

Por exemplo: se o produto usa React Flow para construir funis, aproveite os cards, nós e conexões existentes como referência para criar uma versão 3D. Anime a montagem do funil, a conexão entre as etapas e a navegação pelos componentes, seguindo o que aparece no vídeo.

Crie uma experiência imersiva com animações ligadas à rolagem e interações que façam sentido para o conteúdo. Quando aparecerem nas referências, recrie também painéis laterais, balões de conversa, blocos empilhados e outros elementos da interface.

Priorize acabamento visual, fluidez e legibilidade. Adapte a experiência para desktop e celular, respeite a preferência por movimento reduzido e ofereça uma versão mais leve quando necessário.

Implemente a nova página no projeto, mantendo a estrutura e as convenções do repositório. Verifique a navegação, as animações e a adaptação às diferentes telas.

Quero uma experiência com direção de arte consistente: transforme as cenas do vídeo em uma interface 3D que a pessoa possa explorar.
```

---

## OPC Application Notes

**Potential use:** OPC website — blueprint/project walkthrough section. Instead of a static image gallery, a visitor could scroll through a 3D construction scene (foundation → framing → finished structure) animated to their scroll position.

**Reuse base:** The `oak-park-ai-hub` repo already has web app components (docs/content-creator/, dashboard/) that could serve as the repository reference input.

**Prerequisites before applying:**
1. Identify a reference video that shows the visual style Priscila wants for the OPC 3D scene
2. Decide which OPC website section would host this (likely homepage hero or project showcase)
3. Confirm Three.js is acceptable as a dependency in the OPC website stack
4. Run through CREATIONS Master Build & Lifecycle Plan Section 19 (External Repo/Package Intake Checklist) before adopting Three.js

**Decision status:** RESEARCH CANDIDATE — not yet approved for adoption.
File in Skills & Agents tab of Ideas & Inbox when confirmed for a specific project.

---

## Suggested Next Action (for Priscila)

Watch the reference Reel (Link 5 from the 09/21 saved resources: https://www.instagram.com/reel/DdB9aVqjUE8/) — if it is an OPC-style visual, it could serve as the video reference input for this prompt. If yes, this prompt is ready to use.
