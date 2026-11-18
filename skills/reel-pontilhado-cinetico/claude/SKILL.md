---
name: "reel-pontilhado-cinetico"
description: "Use para reels de checagem/dados no estilo Pontilhado Cinético: palavra-chave grande entrando na hora da fala, fundos com pontinhos, quase sem caixas. Rascunho com voz grátis da Microsoft; ElevenLabs só no final aprovado, 1 take. Também para refazer reels antigos em v2."
---

> **ESTE SKILL EXISTE EM 3 LUGARES:** Mac (`~/ClaudeWorkspace/skills/reel-pontilhado-cinetico/claude/SKILL.md`), Google Drive (Tools, Skills & Flows > Skills > Skills de Reels e Carrosséis > Pontilhado cinético > Claude), GitHub (`priihigashi/oak-park-ai-hub/skills/reel-pontilhado-cinetico/claude/SKILL.md`). Toda alteração deve ser feita nos 3 (e anotada no Skills Tracker).


# Reel Pontilhado Cinético

> **Antes de roteirizar, e já no primeiro vídeo de referência:** seguir também o skill reel-pasta-roteiro-auditoria (pasta v<N>_<slug>, TRANSCRIÇÕES com cada vídeo numerado, linha no tracker, LISTA DE FEEDBACK DA PRIIH no topo do ROTEIRO, roteiro em tabela narração | animação de cada frase, conexões entre blocos, prompt de auditoria). Ele vale junto com este skill.
>
> **Também sempre:** reel-zona-segura (zona do texto + checagem de sobreposição, espremido e quebra de linha) e reel-som (fundo baixinho com 2 opções + sem fundo na prévia, e efeitos especiais nas animações), já na primeira prévia.


Estilo aprovado pela Priih em 20/10/2026 ("muito melhor") na v2 do reel "Comida subiu mais?". Inspirado nos reels do @projeto.contraponto (palavra-chave cinética, textura de pontinhos) e no mapa de conexões amarelo, adaptado às cores da página. Referência viva: artifact "Comida subiu mais? v2". Kit de código no Mac: ~/ClaudeWorkspace/Skills/reel-pontilhado-cinetico/reel-pontilhado-cinetico_kit.zip. Cópia do skill no Drive: Tools, Skills & Flows › Skills › reel-pontilhado-cinetico.

## Ideia central
O texto na tela ACOMPANHA A VOZ: frase-guia pequena em serifa itálica + palavra/número-chave GIGANTE que entra exatamente na palavra falada + figurinha/rosto entrando junto. Nada parado enquanto a voz fala.

## Visual
- Palco 1080x1920. ZONA SEGURA REELS + STORIES (medida nos prints dela, 4/nov/2026): TEXTO só entre x 150-915 e y 268-1680. Imagem, mapa, fundo e efeitos podem ir até a borda.
  - Por quê: no Story a faixa "@ e @collab" + tempo cobre y 0-250; no Reel aberto o Instagram dá zoom ~1,3x (corta ~52 px de cada lado e ~105 px do topo), os botões da direita cobrem x > 930 de y 1060 pra baixo, e perfil/música/legenda começam em y ~1685. A bolha "Drop an emoji" cobre x < 220, y 1460-1550 (passageira): nada importante ali.
  - Área de conteúdo das cenas: y 268-1330 (título/kicker começam em 268, nunca acima).
- Fundos alternando por cena: amarelo #FFD34D, preto #121214, branco neutro #F6F6F4 (nunca bege/creme), vermelho #FF4A3D. Temas pedidos por ela podem trocar o amarelo (ex.: rosa #FF5FA8 no reel de homofobia, 22/out/2026).
- Textura: pontinhos radial-gradient(rgba(20,20,20,.16) 1.4px, transparent 1.8px) a cada 10px (no preto, pontos brancos 9%) + grão de papel (SVG feTurbulence, opacidade .10, multiply).
- Fontes: Figtree 800/900 + Instrument Serif itálico (frase-guia).
- Tamanhos: frase-guia 62px; palavra gigante 150-170px (auto-ajuste para caber em 864px, nunca palavra sozinha na linha); médio 96px; kicker 44px; números de linha 128px; letra miúda 28px; fonte 23px.
- MAIÚSCULA NO COMEÇO DE TODO BLOCO: título, frase-guia, chip, rótulo, legenda de gráfico, item de lista, balão. Só fica minúscula a linha que CONTINUA a linha de cima (classe .cont). Escrever já com maiúscula no texto-fonte e ter também a regra ::first-letter{text-transform:uppercase} nesses elementos, com .cont::first-letter{text-transform:none}.
- Marca-texto desenhado por baixo da palavra (anima de 0 a 100%). Branco no amarelo, amarelo no branco/preto, preto no vermelho, vermelho para "ponto pra crítica".
- Quase sem caixas. Caixas só para carimbo de veredito (VERDADE preto+amarelo, FALSO vermelho+branco) e chips de partido.
- Figurinhas: ícones SVG chapados com contorno branco grosso + sombra + leve balanço. Figurinhas decorativas ficam num canto (ex.: 3-4 bonequinhos no canto direito), nunca cobrindo rosto de quem fala no clipe.
- Rostos: SÓ CABEÇA, grande, contorno branco 7px, balanço. Chip nome · partido · ideologia (azul direita / vermelho esquerda). Presidente atual: "governo atual 🦑 · PT · esquerda", nunca o nome.
- Comparação de governos SEMPRE no mesmo gráfico, azul royal #2D55D6 = anterior, vermelho = atual, com legenda e "como ler".
- Quem governou ao longo do tempo: faixa ano a ano (uma célula por ano) que vai se pintando em sequência, azul = direita, vermelho = esquerda, uma faixa por esfera (prefeitura, estado, país) quando mais de uma importa.
- Números grandes lado a lado começam na mesma altura. Contador animado 0,9s, vírgula decimal, ponto de milhar.
- Animações: rise, pop, slam; barras crescem da base.

## Recorte de rosto (CABEÇA): método que funciona
Na v2 o recorte do presidente atual saiu ruim (foto oficial "ombros" cortava o cabelo; máscara elíptica + corte reto deixou contorno torto e gola). Para os próximos:
1. Foto com a cabeça INTEIRA e folga em volta, de frente, boa luz, alta resolução. Evitar arquivos "cropped"/"ombros"; testar 2-3 candidatos.
2. rembg com modelo birefnet-portrait (ou isnet-general-use) e alpha_matting=True (fg 240, bg 10, erode 10).
3. Só cabeça por landmarks (mediapipe Face Mesh: queixo 152, laterais 234/454). Cortar 4-6% abaixo do queixo seguindo a curva da mandíbula, apagando pescoço, gola e terno. Barba branca: cortar pela mandíbula, não por cor.
4. Suavizar borda do alpha (1-2px) antes do contorno branco.
5. CONFERIR cada rosto sobre fundo amarelo e preto antes de montar. Rosto ruim não vai pro vídeo.

## Clipes de vídeo (fala de político, "TVzinha")
- Cada trecho falado vira um ARQUIVO PRÓPRIO, cortado exatamente no início e no fim da fala (nada de usar um clipe longo e pular pra posição): sem busca de posição, sem tela preta no começo.
- A saída pro fundo é GRAVADA no próprio clipe: ffmpeg fade=t=out (0,45s) para a cor exata do fundo da cena (#121214 no preto), áudio com afade de 0,3s junto. Nada de fade por opacidade no navegador (dá glitch). No fim, o vídeo para no último quadro (que já é a cor do fundo); o chip do nome sai junto (data-out no fim da cena).
- Clipes publicados como arquivos do artifact (não data URI), 540x960, 30fps, keyframe a cada 15 quadros, crf 27, faststart, com pôster jpg. Sincronia leve: buscar posição só ao entrar na cena ou com desvio grande, e nunca buscar enquanto `v.seeking` (buscar a cada quadro trava o vídeo e ele não aparece no celular).
- Voz do clipe mais clara: highpass 90, compressor, loudnorm -13.
- Como pegar o vídeo (funcionou em 22/out/2026): o `capture_pipeline.yml` (transcribe_only) já salva o MP4 na pasta da captura no Drive. Baixar no Composio REMOTE_WORKBENCH com `GOOGLEDRIVE_DOWNLOAD_FILE` (account `priscila`) e `requests` no `s3url`; cortar os clipes com ffmpeg lá mesmo; juntar num .tar de até 5 MB; `upload_local_file` + `GOOGLEDRIVE_UPLOAD_FILE` na pasta da captura; aqui, `mcp__Google_Drive__download_file_content` (limite 10 MB, o base64 vem salvo em arquivo) e `tar xf`. Plano B que também funcionou: empurrar o arquivo em partes de 2,4 MB (`GITHUB_CREATE_OR_UPDATE_FILE_CONTENTS`) numa branch tmp-<slug> e aqui `git clone` + `cat partes`. O shell daqui não alcança Instagram, o R2 nem o backend do Composio; não insistir nesses caminhos. Apagar do Drive as tentativas intermediárias e a branch no fim.
- Recorte do clipe: cortar fora logo da emissora, tarjas e legendas queimadas (elas costumam escrever o nome do presidente). Sem desfoque (vira mancha e pode cair no rosto). Se sobrar logo no canto, cobrir com etiqueta "Vídeo: <emissora>". A nossa legenda troca o nome por [presidente]. Cortar antes de cartelas de divulgação no fim (ex.: datas de show).
- Palavrão em clipe de humorista: bip de 1 kHz baixinho só na sílaba ofensiva, deixando ouvir começo/fim da palavra quando ela pedir (ex.: "chup… [bip] …la"); cobrir a legenda queimada com etiqueta da cor do tema.
- No artifact, vídeo com som não toca sozinho no celular (fica só o pôster). Mixar o áudio dos clipes na trilha principal (adelay no início de cada cena de clipe) e deixar os `<video>` com `muted playsinline`, sincronizados pelo tempo da trilha (buscar posição ao entrar na cena ou com desvio > 0,3 s; destravar todos com play/pause mudo no clique do Play).

## ABA "VÍDEO ORIGINAL" na prévia (vale para todos os formatos de reel, ela 23/out/2026)
Sempre que o reel parte de um vídeo de outra pessoa (link do Instagram, entrevista, fala de político), a prévia ganha uma aba "Vídeo original" com o vídeo inteiro, pra ela assistir e achar outros trechos que valham. Versão leve, feita uma vez só junto com os cortes (no mesmo lugar onde o MP4 já foi baixado, sem gastar outra rodada): `ffmpeg -i orig.mp4 -vf scale=432:768,fps=24 -c:v libx264 -preset slow -crf 32 -g 48 -pix_fmt yuv420p -c:a aac -b:a 64k -ac 1 -movflags +faststart original_leve.mp4` (cerca de 5 MB por 1:30) + pôster jpg. Publicar como arquivo do artifact (não data URI), `<video controls playsinline preload="none">`, sem transcrição nem análise extra. Ao trocar de aba, pausar a trilha da prévia e o vídeo original.

## Bonequinho de corpo inteiro (cabeça real + corpo desenhado)
Quando a cena pede o presidente atual (ou outro político) com corpo, usar o boneco do reel "Vai virar Venezuela?": terno azul-marinho #24305E com calça #1A1F33, camisa branca, gravata vermelha, mãos #F2C9A0, contorno branco grosso; cabeça real (só cabeça) encostada no colarinho, sem pescoço sobrando. Geometria (caixa 320x640): cabeça left 52 top 0 width 216; corpo left 0 top 225 width 320; pernas top 448, left 110 e 164, 46x178; braço solto left 62 top 250, 44x170, girando em `transform-origin:50% 12px`. Nunca terno preto comprido (ela disse que parece juiz). Objeto que ele "tira de trás das costas" (ex.: estrela do PT com "40"): o braço começa atrás do corpo (z-index menor), gira até ~140° e passa pra frente; o objeto compensa a rotação pra o texto ficar de pé.

## Legenda falada
- y 1420, Figtree 800 58px, DUAS linhas por página, máx ~24 caracteres por linha, largura entre x 190 e 915 (fora da bolha de emoji e dos botões).
- Quebrar depois de pontuação; nunca terminar linha em palavra de ligação (o, a, e, em, de, do, da, um, pra, no, que, com); linha mínima ~12 caracteres. Conferir todas as páginas.
- Só a palavra falada fica amarela (fundo claro: palavra amarela sobre fundinho preto).
- Números em algarismos mapeados para a fala: {59%|cinquenta e nove por cento}.
- Gatilhos em número ("w:60", "w:2009") têm que casar com tokens juntados pela voz ("60 bilhões"): o resolvedor aceita prefixo numérico. Conferir que nenhum elemento entra no início da cena por gatilho não encontrado.
- @tentandochegaratevoce em y 1626, fonte em y 1668. Letra miúda nunca abaixo de y 1330.
- Legenda de fala de terceiros (entrevista): transcrever com faster-whisper `medium` (ou `large-v3`) com `word_timestamps=True` num job do GitHub; antes, CONFERIR a duração do áudio enviado (um corte truncado pela metade fez a transcrição parar em 30 s). O SRT do capture_pipeline erra palavras (inventou "adeus, adeus"); nunca usar sem revisar. Trecho inaudível: escrever a melhor leitura e avisar ela.

## Voz (REGRA DURA: Microsoft no rascunho, ElevenLabs só depois da aprovação final, SEMPRE 1 take)
- TODA fala nova, inclusive frases soltas e trocas pedidas no meio das revisões, entra primeiro com voz grátis da Microsoft (edge-tts), com WordBoundary para os tempos por palavra. Só as melhores vozes pt-BR: mulher `pt-BR-ThalitaMultilingualNeural` (a mais natural, padrão), homem `pt-BR-AntonioNeural`; `pt-BR-FranciscaNeural` (rate +12%) como 2ª opção de mulher. Nunca vozes antigas/robóticas. Para acelerar a voz grátis, usar `rate` do edge-tts (ex.: +17%) em vez de atempo.
- Evitar abrir fala com uma palavra solta em pergunta ("Modinha?" soou estranho); preferir frase curta afirmativa ("Não é modinha.").
- Se o edge-tts estiver bloqueado no ambiente: tentar o workaround (item 2 de "Como produzir"). Se não der, Kokoro local (`pf_dora`, speed ~1,36, tempos por sílaba) só como último recurso, AVISANDO que é bem mais robótica e provisória. Nunca gastar crédito por conta própria.
- NUNCA gerar na ElevenLabs até a Priih aprovar o vídeo inteiro com a voz grátis e dizer explicitamente que pode gerar a voz final. "Pode ir até o fim", "coloca", "faz" ou pedidos de ajuste NÃO são aprovação da voz premium.
- Mesmo que o reel já tenha trechos em ElevenLabs (reel antigo), as falas novas ficam na voz grátis na prévia até a aprovação final; a prévia pode misturar as duas vozes.
- Escolher a voz final: NÃO gerar amostras (gasta crédito). Mandar os links grátis `preview_url` do `creative_list_voices` (filtro languages pt, accent brazilian). Voz da biblioteca precisa de plano pago (o dela é pago).
- Final aprovado: ElevenLabs SEMPRE `generations_count: 1` (UM take só, nunca o padrão 4). Tudo de uma vez no fim, cena por cena no mesmo flow (ver abaixo). Nunca repetir a chamada para "tentar de novo" (cobra outra geração). Dizer o custo depois em créditos do plano (ex.: Fumaça em Manaus: ~4.200 créditos). Modelo eleven_multilingual_v2 para pt-BR. NUNCA usar Davi Menegon (`1yAZgIF8C92U9qOmXARZ`): ela achou brusca e robótica (Fumaça em Manaus, 21/out/2026). Voz masculina pedida no reel "Nordeste esquecido" (out/2026): Mark. Opções de mulher para testar: Vanessa (`BQzELs93jJsUOf5rCb9p`), Bruna da Costa (`AKXBn24T1f9tvTDnWzWT`), Christine (`TOXnXBKJSHqTwwqoWW0D`).
- Pra a voz sair natural (lição do Fumaça em Manaus): gerar CENA POR CENA (não o roteiro inteiro num bloco, que sai corrido e sem tom de pergunta), com pontuação marcando as pausas e anos escritos de um jeito que não se misturem ("dois mil e vinte, e dois mil e dezenove"). NÃO inserir silêncio digital entre frases nem cortar o fim das palavras: soa "frase, pausa, frase" robotizado. Acelerar no máximo ~1,1x com `atempo`; acima disso fica metálico. Se precisar de pausa, cortar no ponto mais silencioso com fade curto.
- Créditos: o ElevenLabs não cobra por uso a menos que "usage based billing" ou créditos avulsos estejam ligados; sem isso, quando o crédito acaba a geração para. Falar o gasto em créditos do plano, não em dólar (parece cobrança e assusta).
- Baixar o áudio (o shell não alcança storage.googleapis.com nem o R2 do Composio): `creative_get_flow_run_status` → `content_url` → Composio `GOOGLEDRIVE_UPLOAD_FROM_URL` (se der 403 de limite por minuto, repetir uma vez) → `mcp__Google_Drive__download_file_content` (o resultado grande é salvo em arquivo; decodificar o base64 do campo `content`). Não empurrar áudio para branch do GitHub (bloqueado).
- Tempos por palavra: `creative_add_flow_asset_node` com o generation_id (devolve o node) → `creative_transcribe_audio` (eleven_scribe_v1, custo 0) → baixar o `words.json` completo pelo mesmo caminho do Drive (a lista inline vem truncada) → casar palavra a palavra com o roteiro falado (contar os tokens de cada `{exibido|falado}`), dividir os tempos pelo atempo.
- Trilha suave bem baixa, loudnorm -16 LUFS. Efeitos (fogo, vento, chuva, moedinhas/jackpot) baixinhos, sincronizados nas palavras. Música embaixo da narração: uns 20 dB abaixo da voz (ela achou alta a -16 dB).

## Como produzir
1. Referências do Instagram: abrir no navegador do app no Mac e tirar folhas de quadros com canvas, ou capture_pipeline.yml (transcribe_only).
2. Voz + rostos: branch temporária tmp-<slug> no oak-park-ai-hub via Composio com job.json e workflow on: push que roda edge-tts e o recorte e commita em out/. Só conteúdo público. Baixar com git clone e APAGAR a branch no fim. Esperar uma rodada terminar antes de empurrar a próxima. Se o push for bloqueado pela trava de segurança, não insistir: avisar e usar o plano B da seção Voz.
3. Montar: cenas HTML com gatilhos data-in="w:palavra" (#2 = 2ª ocorrência) ou t:segundos; build.py junta áudio, resolve tempos, gera legenda e embute tudo num HTML.
4. Prévia: artifact celular com Play, barra, botões ↺30s ↺10s ↺5s 5s↻ 10s↻ 30s↻, velocidades 1x / 1,05x / 1,1x / 1,2x / 1,5x / 2x / 3x (sempre todas, já na primeira versão), caixa de anotações (ver abaixo), botão MP4 (após aprovação), aba "Outras opções" (cena mais cheia em 3 estilos: A Pontilhado, B Mapa de conexões, C Vidro), aba "Vídeo original" quando houver vídeo-fonte (ver seção própria) e aba com capa + legenda + 1º comentário + collabs. Mesmo link a cada rodada; versão nova = artifact novo, mantendo as anteriores.
   **Caixa de anotações (obrigatória em toda prévia):** logo abaixo das velocidades, uma caixa "Suas anotações" (textarea) para ela digitar enquanto assiste, com botão **+ Marcar tempo** (insere `[m:ss]` do ponto atual do player) e botão **Copiar** (para colar na conversa). A caixa cresce até ~260 px e depois rola por dentro (`max-height` + `overflow-y:auto`, `resize:vertical`, `box-sizing:border-box`, largura 100%); nunca empurra a página nem cria rolagem lateral. Texto guardado no navegador (localStorage com try/catch, uma chave por reel) para não sumir se a página recarregar.
5. AUDITORIA ANTES DE PUBLICAR, em TODAS as cenas (nunca só na que ela apontou): Playwright percorre cada gatilho e mede (a) sobreposição entre elementos visíveis, (b) texto fora da ZONA SEGURA (x 150-915, y 268-1680; só @ e fonte podem ir de x 150 a 930) ou na bolha de emoji (x < 220, y 1460-1550), e (c) o TEXTO em si, linha por linha (Range.getClientRects de cada nó de texto), porque texto com nowrap vaza da caixa sem a caixa acusar. Qualquer texto passando de x 915 é erro: diminuir fonte ou quebrar linha. Gerar também 2 prints com a moldura simulada por cima (Story: faixas y 0-250 e 1840-1920; Reel: bordas de 52 px, topo 105, botões x>930 desde y 1060, base desde 1685) e mostrar a ela antes do MP4. Conferir também que cada elemento entra na palavra certa (ex.: "Quase 13 mil" entra no "Quase"). Depois, folha de quadros por cena. (Chromium aqui: `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.)
6. Cenas que eu acho cortáveis ganham um aviso tracejado "⚠ Talvez remover" na prévia (some no MP4), em vez de cortar sozinho.
7. Voz ElevenLabs e MP4 só depois do OK final; salvar em motion/ da pasta v<N>_<slug> e anotar NOTE no story doc.

## Render do MP4 (RÁPIDO: ~6 min para 1:45; nunca mais de 15 min)
Lição de 22/out/2026: renderizar quadro a quadro buscando a posição do `<video>` a cada quadro levou ~1,7 s por quadro (1h30 para 1:45) e ela reclamou. O caminho certo:
1. Antes de renderizar, extrair os quadros de cada clipe já na velocidade final: `ffmpeg -i clip.mp4 -q:v 3 fr_clip/%05d.jpg` (30 fps).
2. No modo render, trocar cada `<video>` por um `<img>` com o mesmo estilo (object-fit/position) e, a cada quadro, só trocar o `src` para `fr_clip/NNNNN.jpg` e `await img.decode()`. Nada de `video.currentTime`.
3. Parar o loop de rAF, chamar `render(t)` à mão, e controlar as animações pelo relógio do vídeo: `document.getAnimations()` → `pause()`; transições (`CSSTransition`) com `currentTime = (t − instante em que a classe mudou) × 1000`; animações infinitas (balanço, tremor) com `currentTime = t × 1000`.
4. Palco fixo 1080x1920 (`#frame{position:fixed;left:0;top:0;width:1080px;height:1920px}`, `html,body{overflow:hidden}`), conferir que a largura medida é 1080 (barra de rolagem já deixou 1064).
5. Screenshot jpeg q92 por quadro direto no stdin do ffmpeg (image2pipe mjpeg → libx264 veryfast crf 19). Dividir em 2 metades em paralelo (só vídeo, .mkv), juntar com concat e colocar a trilha inteira por cima no fim (`-c:v copy -c:a aac 192k -shortest`). ~0,2 s por quadro por processo.
6. Testar 2 s antes de rodar tudo, olhar um quadro, e só então mandar o vídeo inteiro em background. Não usar `pkill -f` com padrão que case com o próprio comando (mata o shell).
7. Entregar o MP4 com SendUserFile e copiar para a pasta motion/ do Drive.