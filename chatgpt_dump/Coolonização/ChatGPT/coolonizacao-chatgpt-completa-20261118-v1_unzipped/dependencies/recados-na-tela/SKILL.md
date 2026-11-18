---
name: "recados-na-tela"
description: "Recados vermelhos removíveis na prévia de qualquer reel (talvez cortar, trocar, imagem temporária, outra fala) e o modo \"auditoria com recados\" quando a Priih pedir revisão ou sugestões na tela."
---

# Recados na tela

> **Juntada na auditoria-na-tela (12/nov/2026).** Esta skill virou o "modo leve" da auditoria-na-tela. Ao usar recados, carregar e seguir a auditoria-na-tela; o que está abaixo fica só como histórico. Troca de cena inteira vai pra cards-feedback.

Por quê: a Priih tem dificuldade de ler resposta longa e lembrar de qual cena se trata. O feedback tem que estar NA TELA, em cima da cena, enquanto ela assiste. Vale pra TODAS as skills de reel (e post/carrossel quando houver prévia).

## Como fica
- Etiqueta vermelha (#E5262B), texto branco, borda tracejada branca, cantos arredondados, sombra leve. Começa com um emoji de alerta que diz o tipo:
  - ✂️ **Talvez cortar** (trecho longo, repetido, que não acrescenta)
  - 🔁 **Trocar** / **Imagem temporária · recomendo refazer em IA** (diz o que a imagem final deveria mostrar)
  - 💬 **Outra fala possível** (com a frase alternativa entre aspas)
  - ⚠️ **Conferir** (fato, número, legibilidade, palavra que pode derrubar alcance)
- Uma linha de título + no máximo uma linha curta de explicação. Legível no celular (≥ 22 px no palco 1080x1920).
- Aparece junto com a cena a que se refere (mesmo gatilho de tempo) e some quando a cena sai. Posicionada perto do elemento, sem cobrir a legenda nem o elemento principal.
- Botão fixo na prévia: **⚠️ Com recados / Sem recados** (lembrar a escolha no localStorage com try/catch). Ela consegue assistir com e sem.
- Os recados NUNCA entram no MP4, na capa nem em print de entrega.
- Lista lateral opcional "Recados (N)" com o tempo de cada um, clicável pra pular até a cena.

## Escolher as batalhas
- Na criação normal: poucos, só o que vale a pena (em geral 1 a 4 por reel). Se o vídeo precisa de muita mudança, pode ter mais, mas cada recado tem que valer o tempo dela.
- Nunca cortar ou trocar sozinho o que ela pediu: marcar com recado e deixar ela decidir.
- Imagem temporária sempre ganha recado 🔁, pra não passar despercebida até o final.
- Quando ela responder ("pode tirar", "troca", "mantém"), aplicar e remover o recado na próxima rodada, dizendo em 1 frase o que mudou.

## Modo "auditoria com recados"
Quando ela pedir "auditoria com recados", "não tô gostando, dá uma revisada", "faz sugestões na tela" ou parecido:
1. Rodar a auditoria normal (reel-pasta-roteiro-auditoria + auditoria-dissonancia quando for político): fatos, fluxo, tom, primeiros 10 s, ritmo, cenas paradas, imagens repetidas, quebras de linha, zona segura.
2. Em vez de responder em texto, transformar cada sugestão num recado na cena exata, com tempo. Aqui pode ter mais recados que o normal, mas ainda ordenados por importância (os mais importantes primeiro na lista lateral).
3. Republicar a prévia no MESMO link com os recados ligados. Na conversa, só 1 ou 2 frases: quantos recados e qual é o mais importante.

## Exemplo visual
https://claude.ai/artifact/GiKHumpZ5G7j1QmtuTT5mm (botão "Com recados / Sem recados" no topo).