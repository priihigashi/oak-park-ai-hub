---
name: "reel-estilo-referencia"
description: "Animação 2D desenhada em código copiando o ESTILO de imagens de referência que a Priih manda (traço, cor, textura). Use quando ela pedir 'estilo por referência', '/motion', 'nesse estilo aqui' ou mandar imagens de inspiração."
---

# Reel em estilo por referência (2D desenhado em código)

Ideia de origem: anúncio "/motion" (Kodree, 07/11/2026). A pessoa sobe imagens de um estilo e o Claude desenha e anima cada quadro com código, no mesmo estilo. Não é IA de imagem: é SVG + canvas + JS, então dá pra trocar uma palavra ou um número sem refazer o resto.

Referências guardadas: Drive News > Templates > Estilos e Referências (índice) (1-GV3tr8nm_PRcwCP1ceNNIuhqYo2N2iW). O anúncio, a transcrição e 8 quadros estão em "Estilo por referência · /motion" (1LLgeWSABpgBd8n1VoVti19vaYV834XuM). Doc ÍNDICE: 1LgD1tGqxX-XMGclpkuzM4r5yem549TyYo7GvL5EIiwk. Primeiro teste aprovado como ponto de partida: artefato "Teste de estilo · livro ilustrado v1" (https://claude.ai/artifact/2Rdzua4b4Xe186GDoHCaCQ).

Vale junto com: reel-pasta-roteiro-auditoria, reel-zona-segura, reel-som, reel-fechamento e as regras de reel da Priih (legenda 2 linhas, palavra atual na cor do dia, banner de 0:50, prévia com velocidades e caixa de notas).

## Passo 1: ler o estilo das referências
- Pegar 3 a 6 imagens (dela, ou numa subpasta do índice). Baixar e OLHAR cada uma.
- Escrever uma ficha curta do estilo no ROTEIRO: traço (espessura, cor, se treme), preenchimento (chapado, aquarela, retícula), paleta (hex), textura de fundo, luz, tipo de personagem, ritmo do movimento.
- Nunca copiar personagem, marca ou cena reconhecível de obra de terceiros. Copia-se o estilo, a cena é nossa.

## Passo 2: montar no HTML (palco 1080x1920)
- Fundo: canvas pintado uma vez (manchas com semente fixa, degradê, feixe de luz, grão de papel), escurecendo o rodapé pra legenda.
- Traço: SVG com filtro feTurbulence + feDisplacementMap pra dar o tremido de desenho à mão ("line boil"), MAS bem leve: scale 2, semente trocando 4 vezes por segundo, e só em linhas paradas (varal, prédio, cenário). Nunca em objeto que se move nem em texto: na v1 (scale 5, 8x por segundo, tudo tremendo) a Priih achou que ficou "glitch, meio stop motion".
- Template aprovado pra começar: "Template · livro ilustrado v2" (https://claude.ai/artifact/Si9VZ9tmyAFfUR7pJgUWMp). HTML no Drive (pasta do /motion, template_livro-ilustrado_v2.html) e no GitHub oak-park-ai-hub em docs/templates/estilo-referencia/livro-ilustrado.html. Copiar dele em vez de começar do zero.
- Linhas que se desenham: stroke-dasharray/offset. Objetos pendurados ou que caem: mola amortecida. Tudo em função do tempo t (render(t) puro, sem estado), pra seek e render funcionarem.
- Fonte do texto: Rubik 800 (moderna, forte, levemente arredondada). Título com quebras equilibradas; frase colorida nunca sozinha separada do resto da frase.
- Ocupar a tela inteira até a legenda (nada de tudo amontoado em cima).

## Passo 3: prévia
- Primeiro um trecho de ~10 s sem voz pra ela aprovar o estilo. Gastar pouco: sem agentes paralelos.
- Conferir quadros com Playwright (chromium em /opt/pw-browsers) antes de publicar: sobreposição, cortes nas bordas, quebras de linha.
- Depois do ok: roteiro, voz grátis (Andrew Multilingual ou Thalita), prévia completa, e só no fim voz final e MP4 (skill reel-renderizar).

## Quando não usar
- Se o estilo pedir ilustração muito detalhada (mangá cheio de sombra, pintura realista), o código não chega lá: gerar os personagens no ChatGPT (prompt exato + pasta de referência) e animar em cima.
- 3D: skill reel-3d-historinha.