---
name: "reel-desabafos-notinhas"
description: "Reel no estilo desabafos e notinhas."
---

## Durabilidade e versão ChatGPT · 18/11/2026
Esta é uma cópia versionada para ChatGPT/Codex; o original fica em `../original/`. Antes de concluir uma alteração, preservar nova versão no Drive Creations > Tools, Skills & Flows > Skills > Reels e Carrosséis > formato > ChatGPT (usar as pastas existentes criadas por Claude) E no GitHub privado `priihigashi/news`, em branch/PR sem merge. Conferir arquivo, pasta, tamanho/hash e links nos dois destinos; registrar pendência real se algum falhar. Nunca considerar apenas o arquivo local como entrega durável; GitHub não substitui Drive. Não sobrescrever versões existentes nem alterar a versão Claude. Consultar `MANIFESTO.json` e o índice desta entrega para origem e comprovantes.

As regras atuais de `regras-priih` prevalecem sobre conflitos históricos abaixo, inclusive aprovação antes de MP4 e voz paga. Os arquivos locais citados no texto histórico não são presumidos disponíveis no celular. Dependências preservadas separadamente em `compartilhadas/`, sem fundir os formatos.


# Reel "Desabafos e Notinhas"

> **Antes de roteirizar, e já no primeiro vídeo de referência:** seguir também o skill reel-pasta-roteiro-auditoria (pasta v<N>_<slug>, TRANSCRIÇÕES com cada vídeo numerado, linha no tracker com a coluna Categoria preenchida, LISTA DE FEEDBACK DA PRIIH no topo do ROTEIRO, conexões entre blocos, prompt de auditoria). Ele vale junto com este skill.

Texto em 1ª pessoa num cartão de vidro líquido sobre fundo vivo de ilustrações brasileiras flutuando. Loop perfeito (último quadro = primeiro). Sempre < 60 s. Sem voz; a Priih põe a música no app do Instagram.

## 0. Formato (decidir sem perguntar, salvo se ambíguo)
- **Modo A — Só mensagem (30 s):** cartão com o texto do início ao fim, fundo animado, dissolve e volta ao quadro 1.
- **Modo B — Mensagem + notinhas (59 s):** mensagem 0–30 s; aos ~29,4 s o cartão some; 30–50 s notinhas "DIZEM: …" → resposta alternando em cima/embaixo (uma a cada ~1,8 s, cada uma ~3,5 s na tela); 51–56 s fecho em 3 linhas; 56–59 s dissolve e volta ao quadro 1.
- **Modo C — Carrossel falso (vídeo que parece carrossel), aprovado no "Posta o porquê" (20/out/2026):** moldura do Instagram (avatar + @ + Seguir, contador 1/N, bolinhas azuis, dedo arrastando), cards 1080×1350 deslizando. Cada card fica o tempo de leitura (~0,225 s por palavra, mín. 2 s) + 1 s. Pode misturar humor brasileiro no começo e virar "conversa sincera" no meio. ELA PREFERIU UM ESTILO SÓ do começo ao fim (Pontilhado: pontinhos, palavra gigante, marca-texto, fundos amarelo/preto/branco/vermelho); a virada é marcada só por um card preto ("Agora, sério"). NÃO trocar para vidro verde/azul no meio ("alguma coisa mudou, não gostei"). Desenhos centralizados no card (nada encostado num canto deixando vazio do lado). Desenhos podem se mexer em loop (feed rolando no celular, notificação tremendo, zZ subindo).
Se ela mandar só um texto → A. Se mandar texto + pontos/debunks → B. Se pedir "fingir que é carrossel" → C.

## ★ Entrega para revisão — PRÉVIA AO VIVO (obrigatório, antes de qualquer MP4)
Ela revisa o reel numa prévia publicada como artifact, no celular, não no MP4.
- Kit: repo `priihigashi/oak-park-ai-hub` › branch `feat/collage-reel-format` › `docs/templates/collage_reel/preview_kit/` (README + `mkpreview.py` + `overlap_check.js`). Modelo aprovado por ela: https://claude.ai/artifact/GFQ8SVUf8NmyEb5UNz2VVN ("Querida amiga").
- Montagem: palco 1080x1920 dentro de `#scaler` (nunca escalar `#stage`), escalado para caber no celular (largura ≤ 520 px, 16 px de margem), tema escuro, título "<episódio> · prévia". Este formato não tem narração: usar um mp3 silencioso com a duração exata do reel como relógio (`render(audio.currentTime)`), carregado com `?v=<timestamp>`, para os controles funcionarem igual. Mostrar o loop (ao chegar no fim, volta ao 0).
- Controles obrigatórios: ▶ Play/❚❚ Pausa (`play()` com catch: recarrega o áudio e tenta de novo); barra de busca com `m:ss / total`; botões **↺10s ↺5s 5s↻ 10s↻**; velocidades **1 / 1,05 / 1,1 / 1,2 / 1,5 / 2 / 3x**; teclado ← → pula 5 s (Shift = 10 s), espaço = play/pausa.
- **Caixa de anotações (obrigatória em toda prévia):** logo abaixo das velocidades, uma caixa "Suas anotações" (textarea) para ela digitar enquanto assiste, com botão **+ Marcar tempo** (insere `[m:ss]` do ponto atual do player) e botão **Copiar** (para colar na conversa). A caixa cresce até ~260 px e depois rola por dentro (`max-height` + `overflow-y:auto`, `resize:vertical`, `box-sizing:border-box`, largura 100%); nunca empurra a página nem cria rolagem lateral. Texto guardado no navegador (localStorage com try/catch, uma chave por reel) para não sumir se a página recarregar.
- Publicar com a ferramenta Artifact (page + `files` com stickers/fontes/scripts usados). Cada rodada = republicar no MESMO link com `label` curto e dizer em 1 frase o que mudou. Nunca criar link novo para o mesmo reel.
- Antes de cada publicação: `snap.js` nos tempos-chave (0,5 2 20 32 45 53) olhando os quadros: cartão longe do @, nada sobreposto, leitura, e o ALINHAMENTO NO QUADRO abaixo.
- Painel de postagem embaixo do player (Colagem §6a.8, `preview_kit/post_panel.py`): ⬇ Vídeo MP4 (quando existir), ⬇ Roteiro e ⬇ Capa (desde a 1ª versão, ver CAPA) + campos com Copiar para Legenda do post, Primeiro comentário e Prompt pra checagem (ChatGPT). Publicar com `capabilities: {"downloads": true}`.
- MP4 só depois que ela aprovar a prévia: render → SendUserFile no chat → Drive `motion/` → NOTE datada no STORY doc.
- **Ajustes pedidos = mudança mínima.** Quando ela pede "põe a cara dele do lado", mexer SÓ nisso, sem refazer o layout aprovado (ela: "por que você trocou tanto?").

## 1. Onde vive
- Página-motor: repo priihigashi/oak-park-ai-hub, branch feat/collage-reel-format, docs/templates/collage_reel/desabafo_v2.html (+ DESABAFOS_E_NOTINHAS.md, documentação completa).
- Primeira peça e stickers: Drive News › Reels_Shorts (1IY4TJyv9Dk1qJPdhskyn4flj1g1jp0Kl) › v1_desabafo-contraponto (1MBNaEXlCwReJ1ZouOafR4Sqa-2zh4yrM) › resources/stickers (28 PNGs) e resources/screenshots. STORY doc 1vSwnw9T9g0DjJjJNzw6eZTXPFC_rbZ3T9eXqUlJ43Z4.
- Template doc da Colagem (seção "Desabafos e Notinhas"): 1zzmxjDwmvhUViOnTzR733XWsBS8la2Thag2xbSOBgK8.
- Saída nova: Reels_Shorts › v<N>_<slug>/ com motion/, resources/ e STORY doc (header → HOW TO USE → BRIEF/RESEARCH → SLIDE-BY-SLIDE → LEGENDA → NOTES; revisão = NOTE datada nova).

## 2. Texto
- O desabafo é DELA: corrigir português e clareza, nunca suavizar; pode ficar mais forte. Abreviações de rede (vc, pq, hj) ok.
- A página apoia a esquerda: nada que desminta a esquerda ou "equilibre" com fato fraco. Notinhas = (a) coisas boas que a esquerda fez, (b) atos/falas negativos da direita/PL, sempre com fonte.
- Cada notinha: pílula "DIZEM: frase da direita" + título que responde (dourado no ponto-chave) + 1 frase que explica pra quem não tem contexto + fonte pequena.
- Todo número/fato conferido na fonte primária antes de render (marcar no STORY doc o que ficou pendente). Antecipar o contra-argumento (ex.: "Brasil não é Noruega" → usar SUS, que é nosso).
- Classificação política com cuidado: "60%/75%" do Congresso só fecha contando o Centrão → escrever "contando o Centrão". 1985–2002 = "centro e direita", não "direita".
- Hierarquia: frases-soco em `.h` (título), corpo normal, a frase mais forte em `.rei` com a palavra final em ouro; números em ouro (`.g`). Palavras que não podem quebrar: `<span style="white-space:nowrap">`.
- Número de partido: nunca usar um número de 2 dígitos como piada (pode ser o número de um partido real). Usar 100, mil etc.
- Ganchos inspirados em post de outro criador: manter a sonoridade dela/dele se ela pedir. Crédito na legenda ("Inspirado em @...") só se ela aprovar; perguntar antes.
- Quando o texto cita um caso (ex.: rachadinha), ser ESPECÍFICO com o que foi provado: quantos depósitos, de quanto, onde, em quantos dias, em dinheiro vivo; e por que o caso parou (ex.: anulado por foro, não absolvido). Não inventar motivo que a reportagem não diz.

## 3. Visual (já pronto na página)
- Fundo: gradiente verde-bandeira rgb(0,140,69) ↔ azul royal rgb(20,60,170) com período = duração (fecha loop). Trocar cor: `g1`/`g2` no render (ex.: amarelo).
- Vidro: backdrop-filter blur(22px) saturate(1.7), borda branca fina, cantos 46 px. Fonte Fraunces variável SOFT 100 + Inter (assets/ do @fontsource-variable).
- Abertura: fundo ~0,4 s; cartão aparece sem crescer (fade+desfoque 0,5 s); texto todo em ~1,5 s.
- Stickers: ilustração IA (flux-1.1-pro via replicate_batch.yml disparado pelo Composio GITHUB_CREATE_A_WORKFLOW_DISPATCH_EVENT; prompt "Premium editorial illustration, Brazilian folk art meets contemporary gouache, visible brush and linocut texture, saturated palette deep green, royal blue, warm gold, coral pink, dignified, single subject centered with margin, isolated on plain flat pure white background, no text, no logos"), recorte por flood-fill do branco + borda de papel 14 px + sombra assada; versão _b desfocada. 3 camadas, mesma velocidade (não amontoam), 3 colunas, fases espaçadas. Aparecida sempre na frente e 45% maior.
- Diversidade obrigatória e com dignidade: religiões (Aparecida, baiana de branco, fitinha do Bonfim, evangélica, igreja), LGBT (casais, bandeira, futebol), regiões/trabalhos (vaqueiro, gaúcho, indígena, nissei, motoboy, operário, agricultora, feirante), programas (farmácia, chaves de moradia, merenda, SUS, formanda) sem logo. Nunca duas pessoas do mesmo perfil lado a lado.

## 3a. Rostos (cabeças recortadas) — onde achar SEM baixar da internet
Antes de dizer que falta foto, procurar recortes prontos nos artifacts dela: `Artifact list` → `scope: files` nos posts recentes (ex.: "O Mapa do Flávio" assets/kv/h_*.png, "Flávio Inocente" assets/heads/*.png e assets/props/*.png, "Quem Manda" cut/*.png, "Reel Saidinha" assets/s/h_gov.png) e `Artifact read` com `path` para baixar. Páginas de arquivo único guardam as cabeças como data URI dentro do index.html (ex.: "Comida subiu mais? v2" tem HEADS com o governo atual sorrindo): baixar o index.html e extrair os `data:image`. Escolher a foto mais simpática/neutra (ela reclamou de foto feia do 🦑). Dar contorno branco grosso se não tiver (dilatar o alpha ~8 px). Faltou alguém (ex.: Janja, Lulinha, Michelle): avisar e pedir a foto no chat; nunca círculo vazio com "FOTO".

## ABA "VÍDEO ORIGINAL" na prévia (vale para todos os formatos de reel, ela 23/out/2026)
Sempre que o reel parte de um vídeo de outra pessoa (link do Instagram, entrevista, fala de político), a prévia ganha uma aba "Vídeo original" com o vídeo inteiro, pra ela assistir e achar outros trechos que valham. Versão leve, feita uma vez só junto com os cortes (no mesmo lugar onde o MP4 já foi baixado, sem gastar outra rodada): `ffmpeg -i orig.mp4 -vf scale=432:768,fps=24 -c:v libx264 -preset slow -crf 32 -g 48 -pix_fmt yuv420p -c:a aac -b:a 64k -ac 1 -movflags +faststart original_leve.mp4` (cerca de 5 MB por 1:30) + pôster jpg. Publicar como arquivo do artifact (não data URI), `<video controls playsinline preload="none">`, sem transcrição nem análise extra. Ao trocar de aba, pausar a trilha da prévia e o vídeo original.

## ALINHAMENTO NO QUADRO — vale para os 3 formatos (Colagem, Timeline, Desabafos), ela 19/out/2026
- **Horizontal:** cada bloco ocupa a largura inteira da área útil, da ponta esquerda à ponta direita da linha de referência (na Colagem/Timeline = trilho `.rail` do topo: `left:60px; width:960px` dentro de `.safe`, gráficos `w=960`; no Desabafos = margem de 116 px dos dois lados). Nada encolhido num canto, nenhuma frase quebrando antes do fim da linha. O TEXTO desses blocos continua dentro da zona segura (x 150-915).
- **Vertical:** o conteúdo da tela se espalha no espaço entre o título do capítulo e a legenda, nunca tudo amontoado em cima com um buraco antes da legenda. Na Colagem/Timeline: `window.VFILL = 1390` (y limite, em coordenadas da cena) liga o `vfill` do `layout.js` — o 1º slot (título do capítulo) fica onde está, a sobra vira espaço extra igual entre os blocos seguintes (até +120 px cada) e o que ainda sobrar desce o corpo, metade em cima e metade embaixo. `data-vfill="0"` desliga numa cena (ex.: cena de gancho com composição própria). Na prévia, o `mkpreview` também precisa pôr `window.VFILL`. No Desabafos: centralizar o bloco de texto no cartão e distribuir as linhas número+frase na altura do quadro.
- Cena com muito texto não tem sobra — tudo bem; o limite continua sendo terminar ≥ 60 px acima da legenda.
- Conferir antes de publicar: quadro do FIM de cada cena (tudo já entrou), checagem de sobreposição/margem zerada e mais baixo conteúdo de cada cena perto do limite (não 300 px acima dele).

## CAPA: obrigatória, feita junto com a 1ª versão (vale para os 3 formatos, ela 19/out/2026)
- A capa nasce quando a 1ª versão do vídeo fica pronta, não no fim. Já entra na prévia (imagem ao lado do player + botão **⬇ Capa** no painel de postagem) e acompanha toda republicação. Nunca postar sem capa: no Metricool vai em `videoThumbnailUrl`.
- O objetivo é CLIQUE, não opinião: um gancho que faça os dois lados quererem abrir (modelo: "Há 20 anos a culpa é da esquerda?", que o vídeo depois desmonta). Pode soar como a pergunta ou acusação que a direita faria; a capa não precisa ser a favor da esquerda nem do tema e nunca entrega o veredito.
- Planejada e personalizada por tema: rosto real de quem está em jogo (recortado, sem fundo, com brilho/cor do tema atrás), uma frase curta e um número ou data GRANDE que todo mundo enxerga no feed. Paleta escolhida pelo tema (ex.: rosa e preto para mulheres), não sempre a mesma.
- Sem fato errado e sem número fora de contexto: todo número da capa está no vídeo e tem fonte.
- Texto dentro da ZONA SEGURA Reels + Stories (skill reel-zona-segura: x 150-915, y 268-1680; imagem e fundo podem ir até a borda; conferir com a moldura do Story e do Reel antes do MP4) e legível na miniatura quadrada do grid (miolo central).
- Quando der, fazer 2 opções e deixar ela escolher na prévia.
- Salvar em `motion/` (capa.jpg) e registrar no STORY doc.

## 3b. Tamanhos de partida — cards de texto (Vox / carrossel / Reel de slides)
Começar SEMPRE destes valores (aprovados por ela no "Quem manda há mais tempo?", out/2026). Ajustar pouco a partir daqui, para as peças não ficarem diferentes entre si. Só reduzir se o texto estourar o quadro ou encostar no @ — e conferir no snap.

**Reel 9:16 (1080×1920)**
- Margem lateral: TEXTO entre x 150 e 915 e entre y 268 e 1680 (zona segura Reels + Stories, skill reel-zona-segura, 4/nov/2026); cartão, figurinhas e fundo podem ir além.
- Kicker (rótulo de cima, mono, caixa alta, cor de destaque): 30 px, letter-spacing .18em, top ~268 px (o Story cobre até 250).
- Título: 86 px / 1.02, peso 900, top ~320 px (linhas cheias, sem órfã — rodar noOrphans).
- Linhas número + frase: número 58 px (40 px se for longo, ex. "2% → 13,75%"); frase ao lado 40 px peso 800 / 1.12; nota pequena 28 px (24 px quando são 5+ linhas); gap 30 px, divisória 3 px branca .28.
- Frase de fecho/veredito: 56 px; linhas do tri-fecho ("Há 20 anos…") 38 px.
- Card-grito (SUA!, MORDE A TESTA): até 320 px.
- Legenda de vídeo (citação): 54 px. Quando tiver fala (clipe ou voz): 2 linhas cheias por página e só a palavra atual em amarelo seguindo a voz (Colagem §5b).
- @handle 34 px em y 1748; fonte 24 px em y 1806 (sempre embaixo do @).

**Carrossel 4:5 (1080×1350, classe c45)**
- Margem lateral 116 px; coluna top 92 / bottom 190, gap 14.
- Kicker 26 px; título 78 px.
- Número 54 px (38 px longo); frase ao lado 31 px (36 px estoura os slides com 5 linhas — testado); nota 24 px; gap entre linhas 10 px, padding-top 9 px.
- Veredito 48 px; tri-fecho 34 px.
- Legenda de vídeo 44 px; @handle y 1190; fonte 24 px y 1240.

**Carrossel "extrato contínuo" (Pede pro Flávio, out/2026):** uma tira de papel de extrato bancário (borda serrilhada, linhas pautadas, fonte mono para datas) atravessa todos os slides como panorama de 7560 px fatiado em 7 de 1080; título 94 px e kicker 30 px no amarelo pontilhado acima da tira; carimbos (ASSINADO/PENDENTE) dentro do fluxo, nunca por cima de texto; rostos e objetos (chocolate, ingresso de cinema) encostados na borda de cima da tira.

Tempo de leitura no Reel de slides: ~metade do tempo de leitura completa por card (ela aprovou ~1:27 para 9 cards: 21/3/14/13/11/15/3/3/4 s).

## 3c. Contraste extra — SÓ SE ELA PEDIR
Por padrão não aplicar. Se ela pedir "mais contraste" no texto, aplicar isto (feito no "Quem manda", 19/10/2026):
- Texto pequeno (nota, fonte, perguntas): `text-shadow:0 2px 6px rgba(0,0,0,.85),0 0 2px rgba(0,0,0,.6)`.
- Véu escuro no fundo Vox: `linear-gradient(rgba(0,0,0,.34),rgba(0,0,0,.22) 55%,rgba(0,0,0,.38))`.
- Sombra geral no texto do card: `text-shadow:0 2px 10px rgba(0,0,0,.55)`.
- Cabeças/stickers do fundo: `filter:brightness(.85)`.
- Texto grande (título, números, gritos) normalmente não precisa — ela disse que o grande já estava bom.

## 4. Produção
1. `./setup.sh`; `npm i @fontsource-variable/fraunces @fontsource-variable/inter`; copiar fraunces-latin-full-*.woff2 e inter-latin-wght-normal.woff2 para assets/; stickers do Drive para assets/v2/ (+ _b com GaussianBlur 3). (Google Fonts pode estar bloqueado na sessão: usar @fontsource do npm e embutir em base64.)
2. Copiar desabafo_v2.html para <slug>.html; trocar o texto do #main, `window.NOTAS` (lista [dizem, título, explicação, fonte]) e `window.IMGS`. Modo A: NOTAS vazio, DUR 30, períodos dos stickers 30/15 e fecho/dissolve no fim.
3. `PAGE=<slug>.html node snap.js snaps 0.5 2 20 32 45 53` → conferir cartão longe do @ (y ~1748), sobreposições, leitura, e texto dentro da zona segura (x 150-915, y 268-1680) com a moldura do Story e do Reel.
4. PRÉVIA AO VIVO (seção ★) publicada e aprovada por ela, já com a capa. Só então seguir.
5. Render rápido: dividir em 6 segmentos (script capseg.js: start/end frame) em paralelo, concatenar com ffmpeg concat, depois `-crf 27` (< 30 MB). Sem som. (Alternativa testada: 6 processos Playwright em paralelo tirando JPG quadro a quadro a 30 fps + `ffmpeg -framerate 30 -i f%05d.jpg -crf 22`.)
6. Capa: seguir a seção CAPA (feita já na 1ª versão e mostrada na prévia). Base visual: mesmo fundo + vidro com 2–3 linhas de gancho que fazem os dois lados quererem clicar, sem entregar veredito.
7. Drive: upload por workflow temporário no repo (push num branch tmp-* com o arquivo + workflow que usa secrets.SHEETS_TOKEN, supportsAllDrives=True), ler result.json, apagar o branch (Composio GITHUB_DELETE_A_REFERENCE). Nunca create_file com conteúdo.
8. **Metricool** (blogId 7092974, tentandochegaratevoce, fuso America/New_York): IG REEL + TikTok (title obrigatório) + FB REEL; carrossel = IG POST com várias imagens + FB POST. Colaboradores padrão em `instagramData.collaborators` (Colagem §7) e avisar "convidei esses, mantém ou tira?". Música do catálogo IG falhou por autorização → ela escolhe no app. Sempre mandar a capa em `videoThumbnailUrl`. 1º comentário em `firstCommentText`.
   - **Mídia precisa de link público. Caminho preferido dela: pasta "Metricool public" no Drive** (link aberto, só cópias, com README): copiar os arquivos aprovados pra lá, usar os links no Metricool e apagar as cópias depois. (Registrar aqui o ID da pasta quando confirmado.)
   - **Caminho que funcionou em 20/out/2026:** repo público oak-park-ai-hub. Anexar o repo à sessão (`add_repo` access push), criar um branch órfão sem clonar o repo (`git init` numa pasta de trabalho → `git checkout --orphan tmp-posts-<data>` → copiar só a mídia → commit → `git push <url> HEAD:refs/heads/tmp-posts-<data>`), usar `https://raw.githubusercontent.com/priihigashi/oak-park-ai-hub/<branch>/<arquivo>` no Metricool (ele copia pra static.metricool.com na hora), e apagar o branch logo depois com Composio `GITHUB_DELETE_A_REFERENCE` (o `git push --delete` e a API pelo proxy da sessão falharam).
   - Se a sessão bloquear todos os caminhos: mandar os arquivos pelo chat (SendUserFile) + evento no Google Calendar com alarme no horário, passo a passo e link da prévia. Nunca dizer que agendou sem o retorno do Metricool.
   - "Posta" = publicar agora; quando ela der horário, é agendar naquele horário. Confirmar se "9h45" é AM ou PM quando for ambíguo e tarde da noite.
9. Legenda: começa com COMPARTILHA NOS STORIES + lista Melhores Amigos (ou com o gancho que ela pedir, ex.: "Manda pra alguém que só posta meme"); não citar presidente nem nome de político em hashtag; 1º comentário: COMENTA …, linha ".", linha ".", fontes. Os dois entram no painel de postagem da prévia. Piadas internas do dia (ex.: "Não vamos falar do Felca 🤐" + 1º comentário marcando a pessoa) entram quando ela pedir.
10. STORY doc + NOTE datada; commit da página no branch.
11. Depois de agendar: atualizar os eventos do Calendar para "Conferir: <post> (agendado)" com o link do Metricool.