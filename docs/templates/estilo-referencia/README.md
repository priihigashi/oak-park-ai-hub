# Template: livro ilustrado (estilo por referência)

Animação 2D desenhada em código: traço fino de caneta, cor chapada, fundo de folhagem pintada com luz e grão de papel.
Tudo em função do tempo `render(t)`, palco 1080x1920, prévia com play, busca, velocidades e caixa de notas.

- `livro-ilustrado.html`: template v2 (cena de exemplo: projeto com carimbo de URGÊNCIA pula a fila do varal).
- Tremido de traço (line boil): feTurbulence + feDisplacementMap com scale 2, semente trocando 4x por segundo, só em linhas paradas. Em objetos que se movem ou em texto vira "glitch".
- Regras completas: skill reel-estilo-referencia. Índice de referências: docs/referencias/INDICE_ESTILOS.md.
