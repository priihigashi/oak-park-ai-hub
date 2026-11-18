---
name: "reel-livro-ilustrado"
description: "Reel em estilo livro ilustrado: traço de caneta, cor chapada e fundo pintado (folhagem verde ou céu), animado em código. Use pra historinhas que ensinam, ou quando a Priih pedir livro ilustrado."
---

## Durabilidade e versão ChatGPT · 18/11/2026
Esta é uma cópia versionada para ChatGPT/Codex; o original fica em `../original/`. Antes de concluir uma alteração, preservar nova versão no Drive Creations > Tools, Skills & Flows > Skills > Reels e Carrosséis > formato > ChatGPT (usar as pastas existentes criadas por Claude) E no GitHub privado `priihigashi/news`, em branch/PR sem merge. Conferir arquivo, pasta, tamanho/hash e links nos dois destinos; registrar pendência real se algum falhar. Nunca considerar apenas o arquivo local como entrega durável; GitHub não substitui Drive. Não sobrescrever versões existentes nem alterar a versão Claude. Consultar `MANIFESTO.json` e o índice desta entrega para origem e comprovantes.

As regras atuais de `regras-priih` prevalecem sobre conflitos históricos abaixo, inclusive aprovação antes de MP4 e voz paga. Os arquivos locais citados no texto histórico não são presumidos disponíveis no celular. Dependências preservadas separadamente em `compartilhadas/`, sem fundir os formatos.


# Reel estilo livro ilustrado

Um estilo, uma skill. Origem: abertura do anúncio "/motion" (Kodree, 07/11/2026). Copiamos o estilo, nunca cena ou personagem de terceiros.

## Referências e templates
- Drive: News > Templates > Estilos e Referências (índice) 1-GV3tr8nm_PRcwCP1ceNNIuhqYo2N2iW, pasta "/motion" 1LLgeWSABpgBd8n1VoVti19vaYV834XuM. Doc ÍNDICE 1LgD1tGqxX-XMGclpkuzM4r5yem549TyYo7GvL5EIiwk.
- Templates aprovados: varal do Plenário com pessoas e pomba (https://claude.ai/artifact/6TADAqJa4kBC2VcL7fYLKn) e os exemplos "Como nasce uma lei" e "A mochila que aguenta" em https://claude.ai/artifact/BkybeH3vq5z9zPmSh9CLFd. GitHub oak-park-ai-hub docs/templates/estilo-referencia/.

## Pra que serve
Historinhas que ensinam (série em capítulos, ex.: um projeto de lei de papel que anda da Câmara pro Senado até ser sancionado pelo presidente). Serve pra News, OPC e UGC (produto com perninhas contando a história). Mais caloroso que o motion limpo, bem mais barato que o 3D.

## Visual
- Fundo pintado em canvas com semente fixa: folhagem verde (#55744a para #2a3f25) ou céu (#8fc3dd para #e9dcc0), manchas, feixe de luz diagonal, grão de papel; escurecer topo e rodapé pra ler título e legenda.
- Traço: preto #1b1b1b, linha de pincel que afina nas pontas e varia de leve (função stroke com taper + jitter, ver template).
- Cor chapada: papel #F3EBD8, vermelho #FF4A3D pra carimbo/alerta, cor do dia nas palavras de destaque.
- Tremido de traço (line boil) só em linha parada, scale 2, 4x por segundo. Nunca em objeto que se move nem em texto (na v1 ficou "glitch").
- Personagens: objetos com carinha (dois pontos e boca) e perninhas, pessoas simples de traço, bicho (pomba). Movimento: andar com balanço, mola ao aparecer, câmera que corre de lado.
- Texto Rubik 800, título em cima, legenda de 2 linhas embaixo. Ocupar a tela até a legenda.

## Código do template (copiar daqui)
- Drive, pasta "/motion" 1LLgeWSABpgBd8n1VoVti19vaYV834XuM:
  - template_livro-ilustrado_v3_pessoas.html 17QLPtCs0DYbZHJ2XKOxvNZ6yuR-6KHaq (versão atual, com pessoas)
  - template_livro-ilustrado_v2.html 1jygZZVP7tBqfMZdj6yXDppHq70vbP_WG
  - template_9-exemplos_4-estilos.html 1JqCvM8KhHfQX01dRhDKaIrGpua7hqLvz (motor comum: stroke, painted, paper, person)
- GitHub: oak-park-ai-hub, docs/templates/estilo-referencia/livro-ilustrado.html (v2, PR 320).
- Baixar do Drive e copiar; nunca recriar do zero.

## Como fazer
Seguir reel-pasta-roteiro-auditoria, reel-zona-segura, reel-som e reel-fechamento. Copiar o template, conferir quadros com Playwright (chromium em /opt/pw-browsers), prévia com as regras de sempre. Primeiro um trecho de ~10 s. Personagem muito detalhado sai melhor gerado no ChatGPT e animado em cima.