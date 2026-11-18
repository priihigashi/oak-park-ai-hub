---
name: "auditoria-na-tela"
description: "Auditoria visual do reel com recados na tela (layout, fala, história, dissonância, fatos, ritmo); standalone ou leve dentro das skills de reel."
---

# Auditoria na tela (feedback com recados)

Por quê: a Priih tem dificuldade de ler resposta longa e lembrar a cena. Todo feedback vai NA TELA, em cima da cena, enquanto ela assiste. A resposta no chat fica com 1 ou 2 frases.

Duas formas de uso:
- **Sozinha (standalone):** ela chama quando o vídeo está zoado. Roda TUDO abaixo, com quantos recados forem precisos.
- **Leve, dentro de qualquer skill de reel:** na criação normal, se eu notar algo que vale a pena, coloco poucos recados (em geral 1 a 4). Escolher as batalhas.

## 1. O formato do recado
- Etiqueta vermelha (#E5262B), texto branco em Rubik/Manrope 800, borda tracejada branca, cantos arredondados, sombra leve, ≥ 22 px no palco 1080x1920.
- Começa com o emoji do tipo:
  - ✂️ **Talvez cortar** (trecho longo, repetido, que não acrescenta)
  - 🔁 **Trocar** / **Imagem temporária · refazer em IA** (diz o que a imagem final deveria mostrar)
  - 💬 **Outra fala possível** (a frase alternativa entre aspas, já no jeito dela)
  - 📏 **Layout** (zona, alinhamento, sobreposição, quebra de linha)
  - ⚠️ **Conferir** (fato, número, fonte, palavra que derruba alcance, objeção do outro lado)
- Título de uma linha + no máximo uma linha curta de explicação. Nada de parágrafo.
- Aparece no mesmo gatilho da cena e some quando a cena sai; fica perto do elemento, sem cobrir a legenda nem o elemento principal. Recado de layout aponta o lugar exato (contorno tracejado vermelho no elemento).
- Botão fixo na prévia: **⚠️ Com recados / Sem recados** (escolha lembrada no localStorage com try/catch).
- Lista lateral "Recados (N)" ordenada por importância, cada item com o tempo e clicável pra pular até a cena.
- Recados NUNCA entram no MP4, na capa nem em print de entrega.

## 2. O que auditar (tudo, na ordem)

### A. Layout e texto na tela (o que mais dá errado quando ela pede auditoria)
Varredura com Playwright (chromium em /opt/pw-browsers, fonte de verdade carregada) segundo a segundo e no fim de cada cena, como mandam reel-pasta-roteiro-auditoria e reel-zona-segura:
- **Zona segura:** texto dentro de x 150–915, y 268–1680 (Reel e Story); @ e fonte podem ir até 930; nada na bolha de emoji (x < 220, y 1460–1550). Medir cada linha de texto (Range.getClientRects), não só a caixa.
- **Quebra de linha dos cards e títulos:** nenhuma palavra sozinha, nada de hífen partindo palavra, nome de pessoa não se parte, linhas equilibradas (nenhuma com 1–2 palavras), frase colorida nunca sozinha numa linha; texto corrido vai até o fim do filete (text-wrap: pretty).
- **Páginas da legenda falada:** 2 linhas cheias e EQUILIBRADAS por página (a de baixo mais ou menos da largura da de cima, nunca uma ou duas palavras sozinhas embaixo; nenhuma linha terminando em palavra de ligação), quebra de página em ponto natural da fala (não no meio de nome, número ou expressão), só a palavra atual na cor do dia, sincronia com a voz.
- **Alinhamentos:** números lado a lado começam na mesma altura; blocos alinhados à mesma margem; nada torto sem querer; espaçamentos iguais entre itens iguais.
- **Sobreposição:** nenhuma linha encostando em outra (rótulo de gráfico, carimbo, chip, legenda); nada cobrindo rosto.
- **Ocupação:** conteúdo espalhado na largura toda e até a legenda; sem vão acima da legenda.
- **Tamanhos mínimos:** letra miúda 23 px, notas 24 px, fonte 22 px, sublabels 20 px; letra miúda nunca perto ou abaixo da legenda.
- Maiúscula no começo de todo bloco; texto da tela não repete a legenda no mesmo segundo; frase não aparece logo antes de um corte.
- **Ritmo (regra de 14/nov/2026):** medir em cada cena o tempo PARADO (tudo já entrou, só a voz fala): mais de ~3 s é erro, e eu divido a cena em batidas (sticker, destaque de palavra, troca de elemento ou tela de descanso). Nenhum texto novo no último 1,5 s antes do corte (meio segundo parece glitch). O texto entra no começo da frase que fala dele. Tela com texto demais pra ler em ~3 s: cortar texto, não esticar o tempo. Só a capa de carrossel tem tudo no quadro 0.
- Pessoas: recorte só de cabeça, contorno branco, nome + partido + chip de ideologia; sem iniciais nem placeholder; sem recorte quando o clipe da pessoa está na tela.

### B. Fala (escrita-humana)
- Soa falado ou robô? Frases corridas como conversa ("funcionou porque..."), pergunta e resposta só de vez em quando, tamanhos variados.
- Caçar sinais de IA da skill escrita-humana: travessão, "não é X, é Y" repetido, listas de três, abertura e fechamento de enchimento, palavras de IA, "rapidinho", ritmo certinho demais.
- Números grandes arredondados com "cerca de" (anos exatos); pronúncias (TSE "tê-ésse-é", bets "béts").
- Cada sugestão vira recado 💬 com a frase nova pronta.

### C. História e conexão dos assuntos (roteiro-storytelling)
- Um fio só? Teste do "e aí": se cabe marcador de lista entre as frases, é lista. Blocos que dá pra trocar de lugar = conexão fraca.
- Cada bloco abre respondendo a objeção que o anterior provoca; "mas aí" não conserta lista.
- Primeiros 10 s ensinam algo do tema; o mais importante cabe no primeiro minuto; ponto de checagem a cada uns 15 s; recompensa parcial e geral; o fim volta ao começo.
- Trecho de mais de 5 s sem nada concreto, ou voz falando sem nada novo na tela: recado.
- **Casamento fala x animação (ela reclama toda vez):** montar o mapa de batidas (tempo de cada palavra) e conferir: cada pessoa, número, lista ou objeto citado tem algo entrando na palavra? Lista falada = um ícone por item, em sequência. Faltou: eu FAÇO direto (não é recado), e só aviso em 1 linha o que entrou. Placar/contador tem que contar na tela, não escondido.
- "Qual é o problema disso?" dito cedo e simples; termo técnico seguido de explicação concreta; conclusão dita em voz alta.
- Descrição de cena que ela fez virou fala? Recado pra passar pra animação.
- Peso, não empate.
- **Sementinhas (roteiro-storytelling 8b), sempre, mesmo na auditoria leve:** cena sem sementinha onde cabia uma ganha recado 🌱 com a frase pronta e o lugar (fala, tela ou letra miúda). Termo ou lei citada sem contexto curto (de quando é, o que faz, por que aparece agora) ganha recado 🌱. Fato que não dá pra afirmar entra com ressalva, não sai.

### D. Dissonância (só em reel político ou de notícia)
Rodar a auditoria-dissonancia em versão curta: pros pontos de chance alta, recado ⚠️ na cena exata dizendo como o outro lado vai ler e a saída (prevenir na fala, sementinha na tela, 1º comentário). O relatório completo continua indo pro fim do ROTEIRO como manda aquela skill.

### E. Fatos e regras políticas
A notícia ainda é a mesma? Pesquisar o assunto de novo no dia (votação pode ter acontecido, data mudou); "hoje/ontem" batem com o dia em que vai ao ar? Números, datas, nomes, lado político de cada pessoa; mesmo período nas comparações; de quem é a responsabilidade (cidade, estado, federal); governo atual sem nome; palavras que derrubam alcance.

### E2. Carrossel animado (cards em vídeo)
- O carrossel do Instagram não tem capa separada: o 1º quadro do card 1 É a capa. Card 1 tem tudo na tela desde o quadro 0 (nada entrando/revelando); só movimento de ambiente (brilho ou shake na frase principal que fala com o público, estrelas, faixa).
- Cards 2 em diante podem ter animação de revelar.
- Brilho em fundo vermelho: fechado em volta da palavra e amarelado, nunca névoa branca larga.

### E3. Final com CTA (todo reel News, inclusive coolonização e coolonização BR)
- A última cena tem a frase padrão, palavra por palavra: "Pra ajudar a aumentar o engajamento, copia o link, curte, reposta aqui e nos stories, e segue a página pra não perder o próximo."
- Ícones grandes entrando na palavra falada, nesta ordem: Copia o link, Curte, Reposta (aqui e nos stories), Segue. Sem "Salva".
- Faltou, trocaram a frase ou a ordem, ou o ícone não casa com a palavra: eu corrijo direto e aviso em 1 linha (não é recado). Sugestão de revisor externo (ChatGPT) pra trocar ou cortar essa frase é recusada: é regra fixa dela.
- Quando o tema tem ação cívica, conferir que antes do CTA vem "o que dá pra fazer" com os canais certos e "links e cartinha nos comentários", e que o 1º comentário tem esses links.

### F. Imagem e som
Imagem repetida, imagem temporária sem recado, imagem fraca pro que a fala diz (recado 🔁 com sugestão de troca ou prompt de IA); som alto demais, efeito faltando (reel-som).

## 2b. Painel de opções (destravar o conteúdo)
Quando ela diz que não está gostando, pede auditoria, ou reclama de uma cena ou card específico (mesmo que a reclamação seja sobre outra coisa, tipo quebra de linha ou texto), a prévia ganha uma aba **"Opções"** pra aquela cena/card:
- Primeiro o card como está ("Atual"), e à DIREITA, na mesma linha com rolagem pro lado (nunca linhas separadas embaixo), 3 a 6 alternativas: algumas parecidas (mesmo layout com outro tratamento) e algumas bem diferentes (texto em outro lugar, outro estilo, outra cor, sair do cinético pra algo mais sério, coolonização, palavra vazada etc.).
- Cada alternativa é um card vivo com menu de controles pra ela mexer sozinha: pontilhado sim/não e tamanho (fundo e frente separados), cor, layout, posição do texto, estático ou animado. Vale tanto pra cena animada quanto pra post estático, conforme a necessidade.
- Botão "Usar esta" em cada card, que copia o nome e os ajustes escolhidos pra ela colar na conversa.
- NÃO vem na primeira versão de um reel (gasta muito): só quando ela reclama, pede auditoria ou aponta um card. Na criação normal, no máximo um recado "💡 tenho outras opções pra esta cena".
- Modelo: a prévia "Vibe cool" (https://claude.ai/artifact/GiKHumpZ5G7j1QmtuTT5mm), com o teste ao vivo e os aprovados na mesma linha, e os menus de layout, pontilhado, cor e contraste.
- O que ela aprovar entra na skill do formato (ou na coolonizacao) como padrão, com print.

## 3. Entrega
0. **Recado ou card:** o que eu acho de pequeno (palavra, quebra, tamanho, conferir fato) vira recado na cena. Quando a sugestão é trocar a cena inteira ou o argumento dela, vira card de antes e depois na aba Feedback, seguindo a skill cards-feedback. Esta skill absorveu a antiga recados-na-tela (o modo leve acima é ela).
1. Republicar a prévia no MESMO link (versão anterior preservada) com os recados ligados, mantendo tudo do padrão mínimo (velocidades, pulos, caixa de notas com marcar tempo e copiar, aba do original, download, legenda e 1º comentário).
2. Na conversa, só: quantos recados, o mais importante, e o que eu já corrigi sozinho (layout e quebra de linha eu corrijo direto e o recado vira "✅ corrigido" por uma rodada).
3. Quando ela responder ("tira", "troca", "mantém"), aplicar e remover o recado na rodada seguinte, dizendo em 1 frase o que mudou. Feedback dela entra na lista de feedback do ROTEIRO.

## Exemplo visual
https://claude.ai/artifact/GiKHumpZ5G7j1QmtuTT5mm (botão "Com recados / Sem recados" no topo).