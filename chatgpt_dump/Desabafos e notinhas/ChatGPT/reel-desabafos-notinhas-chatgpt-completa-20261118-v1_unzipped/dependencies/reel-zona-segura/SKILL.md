---
name: "reel-zona-segura"
description: "Zona segura e revisão de quadro final para todos os reels, carrosséis e posts (palco 1080x1920)."
---

# Zona segura: Reels + Stories (palco 1080x1920)

## REVISÃO DO QUADRO FINAL: obrigatória em TODO reel, de TODOS os skills de reel, sem ela pedir (10/nov/2026)
Todo skill de reel aponta pra cá, então esta etapa vale pra todos. Assim que a primeira montagem existir, e de novo a cada versão, ANTES de mostrar a prévia:
1. Print do último instante de cada cena (tudo já na tela) e rodar o verificador de sobreposição nesse instante.
2. Olhar cada print um por um, procurando:
   - **Sobreposição:** texto encostando ou por cima de outro texto, chip, cabeça, desenho ou legenda.
   - **Eixo:** se o elemento principal está no centro (desenho, diagrama, porta), título e textos da cena ficam centralizados. Texto dentro de caixa ou balão é sempre centralizado, com o mesmo respiro dos dois lados.
   - **Linhas equilibradas:** ajustar o tamanho da fonte pra que as linhas fiquem parecidas, sem palavra sozinha nem linha curta no fim (ex.: "Poderes não poderão ser superiores" numa linha, em vez de "Executivo federal." sobrando). Título que cabe numa linha fica numa linha.
   - **Respiro:** texto não encosta em desenho; se faltar espaço, subir a cabeça ou o desenho de cima e o resto sobe junto.
   - **Nome sem pontuação sobrando** no fim da linha ("Davi Alcolumbre ·").
   - **Repetição:** frase na tela que repete a legenda sai.
   - **Buraco:** bloco amontoado em cima com metade de baixo vazia.
3. Corrigir, tirar print de novo, até limpar. Só então publicar.
4. Na mesma passada, revisar o primeiro minuto da narração procurando frase lenta ou comprida que dá pra dizer mais rápido sem tirar conteúdo.

Medida nos prints da Priih em 4/nov/2026 (reel "Bom dia, América" aberto no Reels e compartilhado no Story). Vale para TODOS os skills de reel e capa; quando um skill antigo disser "10% de margem" ou outro número, vale esta regra.

## Vale também pra CARROSSEL e post estático (14/nov/2026)
Toda criação de card (reel, carrossel 1080x1350, post) passa por esta skill ANTES de mostrar. Erros que ela pegou no carrossel do PLP 299 e que não podem repetir:
- **Linha divisória cortando texto:** bloco com posição fixa (top) embaixo de uma grade que cresceu. Bloco que vem depois de lista/grade nunca tem top fixo: calcular pela altura real da grade (offsetTop+offsetHeight+respiro) ou usar fluxo normal.
- **Lista amontoada em cima com buraco embaixo:** lista de itens (checks, números) se espalha até o bloco seguinte; aumentar fonte e espaço entre itens até ocupar o espaço, em vez de deixar vão.
- **Número desalinhado do título do item:** número alinhado com a primeira linha do item (align-items:flex-start), não com a linha de baixo.
- **Bloco encostando no @ / fonte:** respiro mínimo de 1 linha.
- **Lista do reel invadindo a legenda:** o último item termina pelo menos 40 px acima da legenda falada (y 1290).
Conferir com print de CADA card e cada cena com fonte real, olhando um por um, antes de publicar.

## Camadas: texto atrás de quem passa (regra para todos os skills de reel, 14/nov/2026)
- Efeito bom: a pessoa (ou criança na bike) passa NA FRENTE do texto, com recorte da pessoa por quadro. Usar só em cena em que ela se MOVE pela tela (ex.: atravessa da esquerda pra direita, ou vem pra frente e cruza a altura do texto); depois que ela passa, o texto volta a ficar inteiro e legível.
- Nunca em pessoa parada ou sempre centralizada: aí o texto fica na frente ou sobe até sair da cabeça dela, senão ninguém lê a palavra.
- Não em todas as cenas: 1 ou 2 por vídeo.
- Estrela/sticker que cobre rosto nunca da mesma cor (nem parecida) do texto da cena; usar cor de contraste.

## A regra
- **TEXTO** só entre **x 150 e 915** e **y 268 e 1680**.
- **Imagem, mapa, fundo, fogos, efeitos** podem ir até a borda (sangrar).
- @handle em y 1616 e linha de fonte em y 1652 podem ir de x 150 a 930 (ficam logo acima do perfil do Reel).
- **@handle sem fundo (regra dela, 15/nov/2026):** nada de pílula ou caixa escura atrás do @. É só o texto, embaixo de tudo, onde ficaria o comentário: preto em fundo claro (papel, amarelo) e branco em fundo escuro ou colorido (preto, vermelho, terracota, verde), trocando sozinho a cada cena. A linha de fonte fica logo embaixo do @, numa linha só (encurtar o crédito se não couber), terminando até y 1680.
- Legenda falada: entre x 190 e 915 (foge da bolha de emoji e dos botões).
- Nada importante em x < 220, y 1460-1550 (bolha "Drop an emoji", passageira).

## Por quê (o que cobre o quê)
- **Story:** faixa "@ e @collab" + tempo cobre y 0-250; barra de resposta cobre y 1840-1920.
- **Reel aberto:** o Instagram dá zoom ~1,3x, cortando ~52 px de cada lado e ~105 px do topo. Botões da direita (curtir, comentar, repostar, enviar, salvar) cobrem x > 930 de y 1060 pra baixo. Perfil, collab, música e legenda começam em y ~1685.
- **Grid do perfil:** capa vista no recorte 3:4 central (y ~285-1635): título e número grande da capa dentro disso.

## Como conferir antes do MP4 (obrigatório)
1. Playwright mede cada linha de texto visível (Range.getClientRects de cada nó de texto, ignorando opacidade < 0,3) e acusa qualquer uma fora da zona ou na bolha de emoji. Zero erros antes de publicar.
2. Gerar 2 prints com a moldura simulada por cima e mostrar a ela: **Story** (rosa em y 0-250 e 1840-1920) e **Reel** (bordas de 52 px, topo 105, botões x > 930 desde y 1060, base desde 1685), com o retângulo verde da zona segura.
3. Se algo não cabe: diminuir um pouco a fonte, estreitar a caixa ou descer o bloco, nunca jogar texto pra fora da zona.

## Depois de ajustar a zona: sobreposição, espremido e quebra (obrigatório)
Por que existe: no reel dos indígenas (7/nov/2026), ao estreitar o texto pra caber na zona, várias frases ganharam uma linha a mais e passaram a encostar no que vinha embaixo (cabeça recortada em cima do título, letra miúda em cima da frase, selo saindo pela direita, "r" de e-mail sozinho na linha). A Priih teve que apontar tudo por print. Ela não deve precisar.

1. **Verificador de sobreposição** (Playwright, a cada 0,5 s do vídeo inteiro): caixa de cada texto e imagem visível da cena; acusa qualquer par que se cruze mais de 6 px, e qualquer texto que encoste na legenda falada. Zero erros. A cabeça recortada, o NÃO que cai e outras animações planejadas que atravessam a tela são a exceção, e só elas.
2. **Verificador de espremido:** em selo, chip, cartão e item de lista, scrollWidth > clientWidth ou scrollHeight > clientHeight = texto saindo do container. Selo com white-space:nowrap que não cabe: encurtar a frase (ex.: "Trecho da lei derrubado · 2025" virou "Lei derrubada · 2025"), não diminuir até ficar ilegível.
3. **Quebras de linha:** depois de qualquer mudança de largura, olhar cada título e item: nenhuma palavra sozinha na linha ("os", "regra", "48)"), nenhum trecho grifado sozinho numa linha com o resto em outra. Quebrar na mão com <br> quando precisar.
4. **E-mail e link:** nunca word-break:break-all (deixa uma letra sozinha). E-mail longo ganha uma linha só pra ele.
5. **Cabeça recortada e imagem:** se o título ganhou linha, descer a cabeça, o chip e a letra miúda juntos.
6. **Não repetir a legenda:** texto na tela que diz a mesma frase da legenda, no mesmo momento e perto dela, sai.
7. **Espalhar:** cena com tudo amontoado em cima e metade de baixo vazia é erro. Distribuir até perto da legenda.
8. **Rótulo do 3D** (placa desenhada em canvas): a palavra tem que caber inteira na placa; diminuir a fonte do canvas se cortar.
9. **Folha de conferência:** antes de publicar, prints de todas as cenas num momento cheio de cada uma (não só a abertura) e olhar uma por uma.
9b. **Quadro final de cada card, em TODA versão (pedido dela, 10/nov/2026: "tem coisa overlapping em vários"):** pra cada cena, print no último instante antes de trocar de cena, com TODOS os elementos já na tela, e também o verificador de sobreposição nesse instante. Em cada print, olhar: algo encostando ou por cima de outra coisa; frase com palavra sozinha na linha; trecho colorido partido entre linhas; bloco amontoado em cima com buraco embaixo. Pra cada problema escolher a saída que fica mais bonita: aumentar a fonte (preenche o espaço e acerta a quebra), diminuir a fonte (pra caber numa linha só), quebrar a linha na mão com <br>, ou DESquebrar (tirar o <br>/alargar a caixa), ou subir/descer o bloco. Corrigir e tirar o print de novo até ficar limpo. Só depois publicar.
9a. **A auditoria só vale com as fontes REAIS (falha de 10/nov/2026: no celular dela o título quebrou em 3 linhas e encavalou, no print da auditoria cabia em 2):** o Chromium local NÃO baixa Google Fonts, então a auditoria via fonte substituta e quebra de linha diferente. Antes de qualquer print: baixar os .ttf do repositório google/fonts no GitHub (ex.: raw.githubusercontent.com/google/fonts/main/ofl/rubik/Rubik[wght].ttf, e Caveat etc.), copiar pra ~/.fonts, rodar fc-cache -f, e no script conferir document.fonts.check('800 40px Rubik') == true. Se der false, a auditoria NÃO vale: parar e resolver.
9a2. **Auditar CADA ESTADO, não só o fim da cena:** rodar o verificador em todo momento em que entra um elemento (tempo de entrada + 0,7 s, depois da animação), no fim de cada cena e no meio de cada página de legenda. Em cada momento checar: sobreposição de textos/imagens (>6 px), texto fora da zona segura, trecho colorido partido em duas linhas, palavra sozinha na última linha de título/nota, legenda com mais de 2 linhas. Salvar print só dos momentos com problema e OLHAR cada print. Corrigir, rodar de novo até zerar. Só publicar com zero.
9c. **Legenda falada, conferir página por página:** imprimir a lista de páginas; nenhuma página com uma ou duas palavras soltas (ex.: "Nikolas.", "arriscada."), nenhuma página terminando em palavra de ligação (e, de, pra, que...), nome composto e "Estados Unidos" nunca partidos, e no máximo 2 linhas por página. Imprimir a largura de cada linha (cima | baixo): se a de baixo ficar bem menor que a de cima, rebalancear antes de publicar. Número falado por extenso aparece na legenda em algarismo (645, 2026, 88, 10%).
10. **Fonte real no verificador (7/nov/2026):** o Playwright daqui não baixa Google Fonts e mede com fonte reserva mais estreita; passou "zero erro" e no celular a letra miúda encostou no @. Antes de medir, embutir a fonte (woff2 em data URI ou arquivo do artifact) ou rodar a medição na prévia publicada; deixar margem de 1 linha entre letra miúda e @.
10b. **O verificador mede o que aparece, não a caixa do elemento (falha de 15/nov/2026, "Todo mundo de carteira assinada" em cima de "Mesmo sem ser filiado"):** título com transform (scaleY, rotate, scale) fica maior na tela do que a caixa do div que o contém. Medir a caixa do div deixou passar a sobreposição. A caixa de cada elemento é a união do getBoundingClientRect de TODOS os filhos (que já inclui o transform), nunca só o do div de fora. E bloco que vem embaixo de título transformado nunca tem top fixo calculado de cabeça: medir a altura real.
10c. **Texto pequeno, mínimo pra celular menor (pedido dela, 15/nov/2026):** texto que precisa ser lido (chip de quem indicou, rótulo, nota, item de lista, etiqueta de caixa) tem no mínimo 23 a 24 px no palco 1080; nome em chip 26 px. Só letra miúda de fonte e crédito pode ficar em 20 a 22 px. Se aumentar faz o texto quebrar, encurtar a frase ("Ind. gov. atual") antes de diminuir a fonte.
10d. **@handle:** o Instagram já mostra o nome do perfil embaixo no Reel e põe o @ sozinho no vídeo baixado, então o @ fixo em todas as cenas duplica e polui. Mostrar o @ só na cena final do CTA ("segue a página"), sem fundo.
11. Falso alarme conhecido: elemento com entrada "slam" pode aparecer com escala 1,5 no verificador congelado; confirmar no print antes de mexer.

## Montar a página já certa (lição do reel "Fome, 7 milhões", 7/nov/2026: ela não gostou do alinhamento nem das quebras)
A zona segura passou com zero erros e mesmo assim ficou ruim: tudo pequeno, espremido no canto de cima à esquerda, caixas demais, legenda cortando frase no meio. Zero erros no verificador não basta.
- **Uma coluna:** todo bloco começa em x 150 e usa a largura inteira (765 px). Par lado a lado = 2 colunas de 365 (x 150 e x 550). Nada solto fora dessas bordas.
- **Tamanhos mínimos** (palco 1080): frase-guia 64, linha com ícone 58-62 (ícone ~118 px), texto médio 68-92, número/palavra gigante 140-160 (auto-ajuste com nowrap até caber em 765), letra miúda 30, rótulo de gráfico 36-46. Nada de 24 px em texto que precisa ser lido.
- **Poucas caixas:** lista vira linha ícone + texto grande; citação vira texto com barra colorida à esquerda; caixa só pra peça original, carimbo, veredito e post-it.
- **Quebra no texto da tela:** `text-wrap:balance` em todo texto; ` ` entre número e unidade (6,5 mi, R$ 150); `<br>` na mão quando a quebra natural cai errada. Animação com rotação (slam) não vai em texto gigante: a rotação joga letra pra fora da zona.
- **Frase em itálico no topo:** em y 276, não 268 (o itálico sobe ~8 px e acusa fora da zona).
- **Banner "toque pra continuar":** canto de cima à direita (x 600-915, y 262), com a frase curta da cena à esquerda.
- **Card de print com muita gente:** cada item em ~1 linha e meia, 29-30 px, título de uma linha só.

## Legenda falada: uma frase por página
- Centralizada. Toda página tem 2 linhas EQUILIBRADAS (pedido dela, 12/nov/2026): a de baixo com mais ou menos a mesma largura da de cima, nunca uma linha cheia em cima e uma ou duas palavras embaixo. A linha de cima ideal ocupa quase toda a área da legenda. Medir a largura real na fonte (canvas measureText), não contar caracteres, e escolher a quebra que deixa as duas linhas mais parecidas. Preferir virar a página no começo de frase; nunca terminar linha nem página em palavra de ligação (e, de, pra, que, o, a...) nem partir nome composto. Página de uma linha só é exceção (frase muito curta no fim da cena).
- Nomes e expressões que não se partem nem entre linhas nem entre páginas: nome + sobrenome, nomes de programa/entidade (ex.: Pacto Contra a Fome, Mapa da Fome, Bolsa Família), "governo atual", número + unidade.
- Imprimir todas as páginas da legenda em texto e ler uma por uma antes de publicar.

## Números de referência que funcionaram (reel Bom dia, América v15)
Kicker topo 268, título 330, painel 452-1152 (x 165-915), mapa a partir de 1052 (pode sangrar), legenda dos partidos 1512 (x 220-915), rótulo 1572, @ 1626, fonte 1668.