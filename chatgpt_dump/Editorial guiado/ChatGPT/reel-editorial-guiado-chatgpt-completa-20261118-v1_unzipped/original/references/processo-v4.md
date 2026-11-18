# Processo e referência v4

Esta é a documentação histórica da v4 de 16/11/2026, preservada como referência de estilo. O pacote `assets/base-v4/` é portátil para reprodução: todas as imagens estão em `data.js`, e fonte/voz/scripts são locais. Não depende das pastas v2 ou work para abrir. Os antigos construtores descritos abaixo NÃO foram incluídos, pois dependem de caminhos do projeto. Para criar uma nova peça, copie os assets para nova pasta, substitua cenas, fatos, imagens, voz e tempos; gere novos dados sem executar o construtor histórico sobre a referência.

As afirmações de ausência de skill no guia histórico descrevem o momento anterior à preparação deste pacote. A skill se chama `$reel-editorial-guiado`; a presença deste diretório em outputs não significa que já esteja instalada.

# Como repetir o estilo da prévia PLP299 v4

Para repetir em outro chat, cole o pedido pronto no final deste guia e anexe este arquivo. **Não precisa usar o aplicativo Atalhos.** Podemos chamar a receita de **“Prévia editorial PLP”**. Esse é um apelido textual para você pedir o estilo, não uma skill, comando ou shortcut instalado.

## A referência que você aprovou

A referência portátil está em `../assets/base-v4/index.html`, com os arquivos vizinhos. Abra por um servidor local ao revisar.

A v4 tem 12 cenas em 46,464 segundos. Combina títulos animados grandes, recortes autênticos do site e gráficos simples. É montagem editorial de capturas reais, não gravação contínua da navegação. O design aprovado é a referência; os números e afirmações precisam ser conferidos novamente em cada tema.

## A receita visual

- **Formato:** palco vertical 1080×1920, proporção 9:16, redimensionado inteiro para a tela de revisão. No computador, prévia ao lado dos controles; no celular, controles abaixo.
- **Cores:** amarelo #FFD34D, vermelho #FF4A3D, tinta escura #171c2b e branco quase puro #fafbfc. Alternância de cenas claras, amarelas e escuras cria ritmo. O vermelho destaca o convite à participação.
- **Tipografia:** Manrope em peso 800, títulos grandes e compactos, espaçamento apertado entre letras, frases quebradas em linhas equilibradas. Números podem ocupar quase toda a largura. A versão usa um arquivo local `manrope-800.ttf`; não depende de buscar a fonte na internet durante a reprodução.
- **Elementos:** textura pontilhada muito discreta, círculos grandes ao fundo, linha editorial no topo, número da cena, carimbos inclinados, estrela recortada e desenhos vetoriais de documentos. Poucas caixas.
- **Capturas:** janelas com borda escura, cantos discretos e sombra sólida deslocada, como recortes de papel. O enquadramento destaca o ponto citado; não tenta mostrar uma página inteira ilegível.
- **Hierarquia:** título conduz a ideia, imagem explica e legenda acompanha a fala. Linha de contexto/fonte fica em posição fixa. O nome da página aparece na cena final desta v4.

O código coloca o conteúdo principal entre x150–915, começando por volta de y390; cabeçalho em y268, legendas em y1485, identificação em y1626 e fonte em y1668. Esses valores são referência do arquivo atual, não licença para ignorar as áreas cobertas pela interface do Instagram. Conferir cada cena no tamanho real do celular.

## Como o movimento funciona

Os blocos entram de baixo para cima com uma pequena inclinação e retorno elástico. Títulos aparecem palavra por palavra, com cerca de 55 milissegundos entre entradas. Carimbos e recortes chegam em momentos diferentes, em vez de tudo surgir junto. Barras crescem da esquerda para a direita. Estrelas giram suavemente e círculos têm deslocamento discreto.

A cena inicial já aparece montada no primeiro quadro. A animação é calculada pelo tempo da narração, então avançar ou voltar deve reconstruir o mesmo estado visual. A legenda tem duas linhas equilibradas e destaca apenas a palavra falada: amarelo nas cenas comuns, escuro na cena amarela. Ela usa tempos de palavras fornecidos junto à voz, não uma estimativa dividindo igualmente a duração.

Há tratamento parcial de preferência por movimento reduzido. Não tratar isso como auditoria completa de acessibilidade: conferir também contraste, leitura, foco e conforto visual na nova peça.

## Storyboard que deu o ritmo

| Início | Função da cena |
|---|---|
|0s|Número/tema forte, promessa simples e recorte real|
|3,84s|Explicar o benefício: entender por partes|
|7,89s|Mostrar leitura comentada e acesso ao documento integral|
|11,91s|Mostrar explicações abertas|
|15,20s|Voltar às fontes originais|
|17,65s|Comparação visual de hipóteses, com ressalva explícita|
|22,63s|Informar que o material está em revisão|
|24,95s|Convidar o público a ajudar|
|27,37s|Revelar pergunta, sugestão e fato/caso em sequência|
|33,76s|Mostrar o formulário real, sem fazer envio|
|37,80s|Explicar identificação opcional e privacidade|
|42,30s|Fechar com ação curta e endereço|

Em outro assunto, preservar as funções e o ritmo, não copiar automaticamente o texto, os números, a lei ou as promessas de privacidade.

## Ferramentas realmente utilizadas

1. Capturas autênticas do site compõem a matéria-prima visual. O construtor da v4 reutiliza imagens da v2 e uma captura nova do menu. Alguns recursos carregados não aparecem nas cenas finais, por isso a lista de arquivos não substitui conferir o vídeo.
2. **Python** prepara os dados, reúne as imagens e monta o arquivo de cenas. **HTML, CSS e JavaScript** fazem o layout, as animações e os controles no navegador. Os desenhos são **SVG** e CSS. Não há evidência de uso de Canva, After Effects, Remotion ou gerador de vídeo nesta v4.
3. **`edge_tts`**, com a voz grátis **`pt-BR-ThalitaMultilingualNeural`**, gera uma narração contínua e os tempos de cada palavra. A geração depende do serviço disponível e de conexão; não é uma voz executada inteiramente no computador. A reprodução usa o MP3 local.
4. **Web Audio API** oferece dois ambientes opcionais feitos de notas senoidais suaves. A opção inicial é sem trilha. Não há arquivo de música licenciada nem biblioteca de efeitos sonoros nesta versão.
5. A prévia é uma página reproduzível, com play/pausa, posição, saltos de 5/10/30 segundos, velocidades de 1 a 3x, notas com copiar e campos de legenda/comentário. O botão de MP4 fica desativado até aprovação. A prévia HTML não é um MP4 pronto.

## Onde estão os arquivos

Raiz deste trabalho:

`/Users/priscilahigashi/Documents/Codex/2026-11-16/principal-coisa-que-eu-n-o/`

| Caminho a partir da raiz | O que guardar/reutilizar |
|---|---|
|`outputs/apresentacao-site/v4/index.html`|Página da prévia e controles|
|`outputs/apresentacao-site/v4/style.css`|Identidade visual, tamanhos e áreas seguras|
|`outputs/apresentacao-site/v4/preview.js`|Modelos das 12 cenas, movimento, legendas e reprodução|
|`outputs/apresentacao-site/v4/data.js`|Dados e imagens incorporadas usados pela página|
|`outputs/apresentacao-site/v4/cenas.json`|Resumo das cenas e horários|
|`outputs/apresentacao-site/v4/palavras.json`|Palavras e seus tempos|
|`outputs/apresentacao-site/v4/voz.mp3`|Narração grátis desta versão|
|`outputs/apresentacao-site/v4/manrope-800.ttf`|Fonte local|
|`work/apresentacao-site/v4/fala.txt`|Roteiro da narração|
|`work/apresentacao-site/v4/voz.py`|Geração da voz e tempos de palavras|
|`work/apresentacao-site/v4/build.py`|Preparação dos dados e das imagens|

**Para transportar a prévia pronta:** levar a pasta v4 inteira. O `index.html` depende dos arquivos vizinhos; ele não é autocontido. **Para reconstruir:** levar também a pasta de trabalho, as capturas usadas e a fonte. O construtor atual aponta para imagens da v2 e para uma fonte no projeto do site; esses caminhos precisam ser ajustados no novo chat. Não executar o construtor diretamente sobre a v4 aprovada: copiar para uma versão nova.

## Ordem para repetir sem perder o aprovado

Copiar a referência para nova pasta/versionamento. Conferir o tema e suas fontes. Escrever narração curta, contínua e conversada. Planejar as cenas na ordem da fala. Capturar as telas necessárias. Gerar a voz grátis e os tempos. Atualizar cenas, legendas e duração real. Abrir a prévia e assistir inteira, com áudio, no computador e no celular. Conferir cada cena final, cortes, fontes, texto e legendas. Só depois da aprovação preparar eventual MP4 ou voz paga.

Não acelerar a voz para caber. Na v4, tempos de cenas, páginas de legenda e duração estão definidos no código: trocar apenas o roteiro não sincroniza tudo automaticamente. A proporção e os controles devem funcionar desde a primeira versão. Ao hospedar, manter voz, fonte e scripts no domínio permitido, para não repetir o bloqueio de áudio ocorrido com recursos embutidos na versão anterior. A forma de publicação depende do projeto escolhido, não deste apelido textual.

## Pedido pronto para colar em outro chat

> Quero uma **Prévia editorial PLP**, seguindo o guia anexado e a referência visual da v4 do PLP299. Reproduza o estilo: Manrope bold, títulos enormes com linhas equilibradas, amarelo/vermelho/escuro/branco, textura pontilhada sutil, recortes reais com borda e sombra sólida, carimbos, elementos vetoriais e movimento elástico suave. Faça uma prévia vertical 9:16, de 35–50 segundos, com narração grátis contínua Thalita e legenda de duas linhas que acompanha cada palavra. O tema agora é **[TEMA]**, o objetivo é **[O QUE A PESSOA DEVE ENTENDER/FAZER]**, e as fontes/telas são **[LINKS OU ARQUIVOS]**. Preserve os originais e crie uma versão nova. Mostre uma sequência clara, com gráficos apenas quando sustentados pelas fontes. Não reutilize os números do PLP299 sem conferência. Inclua play/pausa, busca, saltos, velocidades, notas e texto pronto para copiar. Entregue uma prévia reproduzível e revise todas as cenas e o áudio no celular antes de pedir aprovação. Não produza MP4 nem use voz paga antes de eu aprovar. Se os arquivos da referência não estiverem acessíveis neste chat, use este guia e a imagem como referência e diga o que precisou reconstruir.

Este guia documenta a receita existente. Nenhuma skill ou automação nova foi instalada, e nenhum arquivo aprovado da v4 foi alterado para produzi-lo.
