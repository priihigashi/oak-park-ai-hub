---
name: "reel-pintado-a-mao"
description: "Reel com foto real transformada em pintura e transições por pinceladas (estilo Liam Perkins). Use quando a Priih pedir pintado, pintura, aquarela ou um antes e depois mais artístico."
---

> **ESTE SKILL EXISTE EM 3 LUGARES:** Mac (`~/ClaudeWorkspace/skills/reel-pintado-a-mao/claude/SKILL.md`), Google Drive (Tools, Skills & Flows > Skills > Skills de Reels e Carrosséis > Pintado à mão > Claude), GitHub (`priihigashi/oak-park-ai-hub/skills/reel-pintado-a-mao/claude/SKILL.md`). Toda alteração deve ser feita nos 3 (e anotada no Skills Tracker).


# Reel pintado à mão

Um estilo, uma skill. Referência: Liam Perkins (Behance, "Down by the Old Railroad" e pintados à mão). Drive: Estilos e Referências > Liam Perkins 1_L58KYs-XbAVp23mBhOR2N8ZUOq4pGeY. Exemplo aprovado como ponto de partida: "Antes e depois pintado" (OPC, obra de Hollywood) em https://claude.ai/artifact/BkybeH3vq5z9zPmSh9CLFd.

## Pra que serve
Antes e depois da OPC com cara de arte, histórias calmas, cenas de lugar (quintal, cozinha, rua). Esconde foto de baixa resolução.

## Como pintar a foto (Python, OpenCV)
- Recortar pra 1080x1920, bilateralFilter(9,60,60) e depois cv2.stylization(sigma_s=80, sigma_r=0.35). Saturar um pouco (Color 1.15).
- Textura de tela: padrão seno leve + ruído (ver template).
- O oilPainting do OpenCV ficou com cara de mosaico: não usar.

## Movimento
- Transição do antes pro depois com pinceladas largas (elipses) que vão cobrindo a tela em faixas, em ordem.
- Texto Rubik 800 em cima, legenda de 2 linhas embaixo, topo e rodapé levemente escurecidos.

## Limite
Código imita a pintura em cima de foto. Ilustração pintada do zero (paisagem inventada, personagem pintado) sai melhor gerada no ChatGPT com prompt exato + referências da pasta, e animada em cima.

## Código do template (copiar daqui)
- Drive, pasta "/motion" 1LLgeWSABpgBd8n1VoVti19vaYV834XuM: template_9-exemplos_4-estilos.html 1JqCvM8KhHfQX01dRhDKaIrGpua7hqLvz (antes e depois pintado, função painted()). Prévia: https://claude.ai/artifact/BkybeH3vq5z9zPmSh9CLFd
- Pintura da foto: OpenCV bilateralFilter + cv2.stylization (oilPainting fica mosaico).

## Como fazer
Seguir reel-pasta-roteiro-auditoria, reel-zona-segura, reel-som e reel-fechamento. Conferir quadros com Playwright antes de publicar a prévia.