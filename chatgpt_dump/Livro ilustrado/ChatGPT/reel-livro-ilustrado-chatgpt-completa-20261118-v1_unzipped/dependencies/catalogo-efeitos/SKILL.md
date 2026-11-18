---
name: "catalogo-efeitos"
description: "Use quando a Priih descrever uma cena de reel e pedir ideias de efeito/estilo, ou mandar referência nova de efeito pra catalogar."
---

# Catálogo de Efeitos

Onde fica:
- Drive: News > Templates > Catálogo de Efeitos e Estilos (índice), pasta 1-GV3tr8nm_PRcwCP1ceNNIuhqYo2N2iW. Subpastas 01 Texto e tipografia, 02 Rastreamento, 03 Ilustrado e desenhado, 04 Motion e infográfico, 05 Colagem e recorte, 06 3D, 07 Som, 08 Repos e skills grátis.
- Doc índice: 1LgD1tGqxX-XMGclpkuzM4r5yem549TyYo7GvL5EIiwk (só acrescentar, nunca apagar).
- Catálogo visual: https://claude.ai/artifact/JtaavfuNGWT3wSoJxa9vvj (dados no HTML; republicar no mesmo link quando entrar efeito novo).
- Laboratório texto atrás / dedo / rosto: https://claude.ai/artifact/PY6pNZtEryArPajU9r46K6

## Quando ela diz "tenho essa cena, me dá 3 sugestões"
1. Leia o doc índice e os dados do catálogo.
2. Dê 3 sugestões de tipos diferentes (ex.: um gancho, um explicativo, um de fechamento) e um "misturadão" que combine.
3. Para cada uma: nome, por que serve pra cena, de onde vem (skill nossa, repo grátis, recriado).
4. Não pare no texto: ela é visual. Monte a prévia HTML da melhor (ou das 3 lado a lado, curtas) seguindo as regras de reel dela.

## Quando ela manda referência nova (link de reel/post)
1. Baixe o vídeo você mesmo (yt-dlp no workbench; se bloquear, pipeline do oak-park-ai-hub).
2. Transcreva e tire quadros. Salve na subpasta certa: vídeo leve, LEIA com transcrição, quadros.
3. Pesquise se existe grátis (GitHub, Gumroad grátis, HyperFrames registry, iart-ai, Remotion templates). Confira licença.
4. Se não existir, recrie (HTML/MediaPipe/Three.js) e publique uma prévia.
5. Acrescente linha no doc índice e uma entrada no catálogo visual.

## Fontes grátis já baixadas (pasta 08)
- HyperFrames (HeyGen, Apache 2.0): skills + 448 peças (legendas, texto atrás com profundidade, anotação à mão, mapas, gráficos, transições, cards sociais).
- iart-ai motion skills (MIT): tipografia cinética, legendas TikTok, mapas, gráficos, quadro branco, isométrico, tarja de nome, conversa de chat.
- Remotion templates RVE (81, MIT), SwiftClip (32, MIT), Curvable (MIT). Remotion: grátis até 3 funcionários.

## Técnica do texto atrás da pessoa
MediaPipe selfie segmentation (Apache 2.0): fundo, depois texto, depois a pessoa recortada por cima. Dedo: Hands, ponto 8. Rosto: Face Detection modelo full. No artifact os modelos vão embutidos em .js (o servidor não serve .tflite).