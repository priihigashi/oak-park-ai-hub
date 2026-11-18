---
name: "reel-colagem-jornalistica"
description: "Reel no estilo colagem jornalística."
---

## Durabilidade e versão ChatGPT · 18/11/2026
Esta é uma cópia versionada para ChatGPT/Codex; o original fica em `../original/`. Antes de concluir uma alteração, preservar nova versão no Drive Creations > Tools, Skills & Flows > Skills > Reels e Carrosséis > formato > ChatGPT (usar as pastas existentes criadas por Claude) E no GitHub privado `priihigashi/news`, em branch/PR sem merge. Conferir arquivo, pasta, tamanho/hash e links nos dois destinos; registrar pendência real se algum falhar. Nunca considerar apenas o arquivo local como entrega durável; GitHub não substitui Drive. Não sobrescrever versões existentes nem alterar a versão Claude. Consultar `MANIFESTO.json` e o índice desta entrega para origem e comprovantes.

As regras atuais de `regras-priih` prevalecem sobre conflitos históricos abaixo, inclusive aprovação antes de MP4 e voz paga. Os arquivos locais citados no texto histórico não são presumidos disponíveis no celular. Dependências preservadas separadamente em `compartilhadas/`, sem fundir os formatos.


# Reel — escolher formato e produzir a COLAGEM JORNALÍSTICA

## REGRA DURA: nunca o @ de quem espalha desinformação (ela, 30/out/2026)
É terminantemente proibido divulgar o @ / nome de usuário de quem está espalhando fake news (não é "errou um pouquinho": está espalhando desinformação). A gente não compartilha nem promove essas pessoas, nem manda gente pra página delas.
- Proibido em QUALQUER lugar: linha de fonte na tela, legenda do post, 1º comentário, título do TikTok, hashtags, marcação de pessoas, convite de collab e capa.
- Pode: nome + partido + ideologia no chip (ex.: "Nikolas Ferreira · PL · direita") e "o deputado" na fala/legenda.
- Fonte do vídeo checado fica sem @: "Vídeo do deputado no Instagram, 28/10/2026".
- Antes de agendar: procurar o @ do autor no gerador, na legenda e no 1º comentário; não agendar enquanto aparecer.

## 0. Primeira coisa: perguntar o formato (uma pergunta, com opções)
Use AskUserQuestion (ou texto, se ausente):
- **Dinâmica / Checagem ao Vivo** — tem vídeo de alguém falando: vídeo original + legenda PT-BR palavra por palavra + pop-ups e carimbos (template doc 1DTh721k2WZm8z4Ps2521fPHS7EAlCMEve-Nxhn6chw8 — ler inteiro, com NOTES).
- **Colagem** — tema é número/comparação/dado, ou refazer vídeo de outra página: 100% gráfico (fundo chapado com textura de papel, rostos em sticker com borda branca, objetos recortados, contadores, recorte de jornal, carimbos, barras/colunas que crescem).
Perguntar também: **com voz ou sem voz?** (padrão: com voz) e, se fizer sentido, **qual variação visual** (ver §1b).
Se ela não estiver presente: Colagem quando não houver vídeo-fonte bom; Dinâmica quando houver; com voz.

## 1. Onde as coisas vivem
- Motor/template: repo `priihigashi/oak-park-ai-hub` › branch `feat/collage-reel-format` › `docs/templates/collage_reel/` (README = flow completo, `REPERTORIO.md` = catálogo de movimento, `reel.html` = episódio 1, `engine.js` = motor, `fx.js`+`fx.css` = repertório extra, `layout.js` = empilhamento sem sobreposição + distribuição vertical (`vfill`), **`fit.js` = títulos sem estouro (ver §5c)**, `repertorio.html` = demo de todos os presets, `setup.sh`, `demo_assets.sh`, `capture.js`, `snap.js`, `audio.py`, `cutout.py`, `linescreen.py`, `svg2png.js`, `preview_kit/` = prévia ao vivo, ver §6a; `preview_kit/text_check.js` = checagem linha por linha).
- Doc TEMPLATE da Colagem: Drive › Videos › `colagem-reel-template` (13OJNMGCR6oFHYuX_xsLznlSr3qwQdC8a) › doc 1zzmxjDwmvhUViOnTzR733XWsBS8la2Thag2xbSOBgK8 (ler inteiro, com NOTES). Referências estudadas: `repertorio/ref_NN_<pagina>/` (1jr2YlJZlo0Z2Ynxj7LLgWDxq02bZM08a).
- Saída: Drive News › Reels_Shorts (`1IY4TJyv9Dk1qJPdhskyn4flj1g1jp0Kl`) › `v<N>_<slug>/` com `motion/`, `resources/` e o STORY doc (header → HOW TO USE → BRIEF/RESEARCH → SLIDE-BY-SLIDE → LEGENDA → NOTES; revisão = novo bloco NOTE datado, nunca editar notas antigas).
- Exemplos prontos: v1_comida-subiu-mais (`16nHwi5YIPWFZu8bkXuprGK4vTJ_r-Dej`), v3 com voz. **Referência de design favorita dela: "Querida amiga" (prévia https://claude.ai/artifact/GFQ8SVUf8NmyEb5UNz2VVN, fonte `qamiga.html` + `preview_kit/gen.py`) — usar como base de visual, espaçamento e ritmo.** Reel do Rio (`preview_kit/gen_rj.py`, `data/rj/`) = referência de gráficos que acompanham a voz (§5e), largura, distribuição vertical, rodapé e legenda (§5b e ALINHAMENTO).
- Tokens de marca (atualizados 16/out/2026): amarelo #FFD34D · vermelho #FF4A3D · branco · fundo escuro #0E0D0B/#050608. Governo anterior = azul royal #3156D3. NADA de azul acinzentado/ardósia. Fontes do kit: Rubik 900/800/500 (títulos e legenda), Caveat (letra de mão), JetBrains Mono (fontes/etiquetas). Verde/vermelho de veredito continuam só em veredito.

## 1b. Repertório de movimento (ela gosta de MUITO movimento, edição variada e fontes diferentes)
Além do motor clássico (slam/pop/drop/up/left/fade/stamp/.cnt/.bar/.col/data-bob/data-o/data-shake), usar o fx.js:
- Entradas: `glitch` · `scatter` · `dissolve` · `iris` · `down` · `flash`; saídas `data-out="glitch|dissolve|scatter"`.
- Contínuos: `data-boil` (tinta fervendo) · `data-kb` (Ken Burns) · `data-drift` · `data-jit` · cena `data-vhs`; transição de cena `data-in="cut|fade|glitch|wipe"`.
- Componentes: `.kar.karfull` legenda karaokê (OBRIGATÓRIA com voz; páginas de 2 linhas cheias, só a cor amarela anda — ver §5b; `data-words="palavra:t ... / nova página"`, tempos vindos da voz) · `.stack` · `.knock` · `.burst` · `.torn` · `.webcard` · `.sil` · `.glass` · `.label` · `.letter`.
- Contadores: `data-thou="1"` = ponto de milhar (1.571).
- Fotos: `linescreen.py` (retícula de linhas B&W) unifica fotos ruins.
- Variações de template: Palavra por batida · Retícula · Quadrinho · Antes/Depois de manchete · Híbrido Dinâmica+karaokê · Tela dividida EUA×Brasil (2 metades de foto + chip numerado no meio).
- Regra: nunca cena com só um tipo de entrada; misturar 3+ presets por reel; algo muda a cada 1,5–3 s.

## 1c. Quando ela manda um vídeo de referência para "aprender" (não para refazer)
1. Quadros 1 fps + tiras 6 fps por trecho + 24 fps nas transições; medir energia de movimento por segundo (corte seco x movimento contínuo). Foco no MOVIMENTO, edição e fontes — não nos quadros parados.
2. Mapear cada movimento a preset existente; o que faltar vira preset novo em fx.js (documentar no cabeçalho), sem mudar o render dos episódios antigos (testar diff de pixel).
3. Cena nova em repertorio.html + render do demo (capture.js + audio.py) e enviar no chat.
4. Atualizar REPERTORIO.md + commit no branch; doc TEMPLATE ganha bloco REF NN + NOTE datada; quadros/tiras/demo em `repertorio/ref_NN_<pagina>/` no Drive (repo é público: nada de print de terceiros no repo).
5. Quando ela manda um reel NOSSO já publicado como referência (ex.: SP), comparar cena a cena com o reel em produção: o que o outro faz melhor, o que o nosso faz melhor, inconsistências entre os dois — e aplicar sem desfazer o que ela já aprovou.

## 2. Pesquisa (antes de abrir o template)
1. Se veio vídeo de referência: extrair quadros 1 fps + transcrição; listar o que funciona e onde peca (fonte partidária? período escondido? gráfico sem escala? causa sem prova? peça de campanha?).
2. Checar cada número na FONTE PRIMÁRIA (IBGE/SIDRA, BCB, DIEESE, TSE, Câmara/Senado, FAO, MAPA). Dar o benefício da dúvida: se o número bate, dizer que bate.
3. Achar o que falta de bom (dado que reforça) E o ponto honesto contra (o que é verdade no lado acusado). Os dois entram no vídeo.
4. Ângulo político da página (não é só o tema do vídeo original): ex. quem reclama do governo e recebeu recorde (agro / governador).
5. Ler Placar do Congresso e os TXT/briefs do Drive do tema antes de inventar pauta.
6. Fotos: Wikimedia Commons (busca com `filetype:bitmap`), Agência Brasil, Planalto, Senado — registrar licença e autor de cada uma. Se o shell não alcança a Wikimedia, baixar pelo workbench remoto do Composio e trazer por um branch temporário do repo PRIVADO `priscila-workspace` (apagar o branch depois).
7. Clipes reais de imprensa (NBC, CBS, VideoPress do Intercept): o shell não alcança; usar um workflow temporário sem segredos num branch `tmp-*` que roda `yt-dlp` (+ `ffmpeg -nostdin` dentro de loops `while read`, senão o loop para no primeiro arquivo) e faz commit dos arquivos (≤45 MB, reduzir para 720 px). TikTok e Reddit bloqueiam IP do GitHub. Transcrever no runner com faster-whisper (decodificar o áudio com ffmpeg para numpy; o PyAV do runner quebra). Nunca colocar URL assinada (ElevenLabs/Google Storage) em arquivo do repo: baixar pelo workbench e subir o arquivo em si. Apagar o branch no fim.
8. Quando a tela diz que algo mudou ("recua desde 2020", "caiu"), a narração ou a letra miúda diz POR QUÊ e QUEM fez (polícia estadual, PF, MP, briga interna, outra facção), com o governo de cada esfera na época — senão o público credita a quem não fez.

## 3. Roteiro (60–85 s; com voz pode passar ~15% do original)
Antes de tudo, escrever a história em duas passadas (skill reel-pasta-roteiro-auditoria, passo 0): primeiro o fio contado como conversa, depois as regras. Os itens abaixo são os ingredientes de uma checagem, não uma fila de frases: cada um entra ligado ao anterior ("só que", "mas aí fui conferir", "e comparado com o quê?"). Se a fala virar um item por frase, fica robótica (foi a queixa dela na v1 das bets, nov/2026).
1. 0–4 s GANCHO que ACUSA (recorte de jornal + rosto): afirmação precisa e falsificável. Capa nunca entrega o veredito; os dois lados têm que querer clicar (ver CAPA).
2. "SERÁ? BORA OLHAR OS NÚMEROS" + fontes na tela.
3. Admitir o que é verdade (carimbo VERDADE).
4. "Ponto pra crítica" (dado contra o lado que vai ganhar).
5. "Comparado com o quê?" — cara a cara, mesmo índice, meses de cada lado.
6. 3–4 blocos de prova (contador → gráfico → fonte). Algo muda na tela a cada 1,5–3 s; nada parado >4 s.
7. Ângulo político.
8. Veredito ~85%: volta o recorte do gancho + FALSO (ou ENGANOSO se for meia-verdade) + "O TÍTULO DESTE VÍDEO TAVA ERRADO."
9. Fechamento: VERDADE/FALSO resumido + "antes de repassar, confere o período e a fonte" + pergunta pra comentar.

## 4. Voz (narração)
- A fala de cada cena sai do roteiro corrido (frases ligadas, tamanhos diferentes); números por extenso ("cinquenta e seis por cento"). Para sincronizar itens em sequência, ancorar cada item na palavra que o cita (tempos por palavra), em vez de quebrar a fala numa frase curta por item: isso deixava a narração picada e robótica.
- Vozes: ElevenLabs **Mark** (`UgBBYS2sOqTuMpoF3BR0`, narrador), **Athena** (`fpqzllOdDmER4wwFESLO`, moça, PT-BR; é voz da biblioteca, não clone dela) e **Bruna da Costa** (`AKXBn24T1f9tvTDnWzWT`, moça PT-BR, usada no reel da saidinha em 20/out/2026). Alternativa testada: Aline – Warm & Narrative (`hDHD10Ms9Fhra3KMKKkc`). **NUNCA usar Davi Menegon** (`1yAZgIF8C92U9qOmXARZ`): ela achou brusca e robótica (Fumaça em Manaus, 21/out/2026). Pelo conector ElevenLabs (creative_generate_speech, modelo eleven_v4). Checar créditos antes.
- **REGRA DURA DE VOZ (vale para todos os reels):** rascunho SEMPRE com voz grátis da Microsoft (edge-tts); ElevenLabs só depois que ela aprovar o vídeo inteiro e disser explicitamente que pode gerar a voz final. Pedido de ajuste, "coloca", "faz" ou "pode ir até o fim" NÃO é aprovação da voz final.
- ElevenLabs: SEMPRE `generations_count: 1` (UM take só, nunca o padrão 4; crédito é caro). Nunca repetir a chamada para "tentar de novo" (cobra outra geração). Antes de gerar, dizer o custo estimado em créditos do plano (não em dólar: o ElevenLabs só cobra a mais se "usage based billing" ou créditos avulsos estiverem ligados). Gerar tudo de uma vez só no fim, uma fala por cena no mesmo flow (o roteiro inteiro num bloco sai corrido e sem tom de pergunta).
- Pra ela comparar vozes: NÃO gerar amostras (gasta crédito). Mandar os links grátis `preview_url` que o `creative_list_voices` devolve.
- **Baixar o áudio do ElevenLabs (o shell não alcança e URL assinada não pode ir pra repo):** `creative_get_flow_run_status` dá `content_url` de cada take → Composio `GOOGLEDRIVE_UPLOAD_FROM_URL` direto pro `resources/` do reel (lotes de 3–4, senão estoura o limite por minuto do Drive) → `mcp__Google_Drive__download_file_content` (o resultado grande é salvo em arquivo; decodificar o base64 do campo `content`). A chave ElevenLabs do repo (segredo do GitHub) é de conta grátis e NÃO usa vozes da biblioteca.
- **Tempos por palavra da voz final:** `creative_transcribe_audio` (eleven_scribe_v1, custo 0) com `connect_from` = node da fala no mesmo flow; os `words` (start/end) alinham com o texto do roteiro (difflib), interpolando só o que não casar (`tools/align_scribe.py` do reel da saidinha). faster-whisper local não baixa modelo (Hugging Face bloqueado).
- Nomes estrangeiros: escrever como se fala na voz PT ("Renê Gud", "Kristi Nôum", "Djórdj Rétes") e corrigir a grafia na legenda. Siglas que se falam como palavra (ONG) também vão no dicionário de pronúncia. Números de projeto de lei por extenso na fala ("mil cento e doze").
- Voz de rascunho (padrão de todo reel até a aprovação): Microsoft neural pt-BR via `edge-tts`, SÓ as melhores: mulher `pt-BR-ThalitaMultilingualNeural` (a mais natural), homem `pt-BR-AntonioNeural`; `pt-BR-FranciscaNeural` como 2ª opção de mulher. Nunca vozes antigas/robóticas. WordBoundary dá os tempos por palavra. Se o edge-tts estiver bloqueado no ambiente: Kokoro (`data/rj/tts_align.py`, pf_dora) com tempo real por alinhamento forçado (DTW), avisando que é bem mais robótica e só provisória. Palavras curtas soltas ("Falso.", "Pausa") saem com sotaque espanhol/francês na Multilingual: escrever frase inteira ("Isso é falso.", "Dá uma pausa no vídeo").
- Opção antiga: workflow `replicate_batch.yml`, `minimax/speech-02-hd`, `Casual_Guy` (ela achou com sotaque de Portugal; usar só se pedir).
- Voz natural: gerar cena por cena com pontuação marcando as pausas; nunca inserir silêncio digital entre frases nem cortar o fim das palavras (fica "frase, pausa, frase" robotizado); se precisar de pausa, cortar no ponto mais silencioso com fade curto.
- Pós-processo: cortar silêncio das pontas, atempo ~1,1. A voz do ElevenLabs é mais lenta que a provisória: pra manter a duração aprovada precisa de atempo maior (saidinha: 1,45); avisar a velocidade usada. Pausa entre cenas e entre clipes curta: ~0,06 s antes + ~0,1 s depois de cada fala (ela, 20/out/2026: "não precisa ter pausa entre os clipes"); final +1,0 s.
- Quando ela pedir "mais rápido X pontos": somar X/10 na velocidade de TUDO (narração E clipes reais; clipes com `setpts=PTS/k` no vídeo e `atempo=k` no áudio).
- Trecho que ela achar rápido demais: desacelerar só aquele pedaço (atempo ~0,85 no trecho, cortando em silêncio) e compensar o tempo nas pausas, sem passar da duração máxima.
- Tempos por palavra da voz → `data-words` da legenda `.kar.karfull`. Cada elemento na tela entra na palavra que o cita (nunca antes da fala). Ao ancorar num número por palavra, conferir que a palavra não aparece antes na mesma fala (ex.: "cinco" de "noventa e cinco" fez o gráfico entrar na hora errada).
- A prévia SEMPRE toca o `narracao.mp3` recém-mixado (o mesmo que gerou a linha do tempo); conferir que a duração do áudio bate com `window.DUR` antes de publicar — áudio velho = tudo fora de hora.
- Música de fundo suave (pad + pulso leve + whoosh discreto na troca de cena), abaixada embaixo da voz (ducking), cortada na duração exata da narração (`tools/music.py` do reel da saidinha). Ajuda a pessoa a ficar até o fim; nunca briga com a voz. Em checagem de mentira (tema sério/triste): trilha séria, nunca alegre (ex.: "Investigations", Kevin MacLeod, CC BY 4.0, crédito no 1º comentário); nada de synth zumbindo.

## 5. Regras
- Fonte (instituição + série + período) em todo número, mono pequena, SEMPRE na mesma linha embaixo, longe do conteúdo. Nunca com o @ de quem espalha desinformação (ver REGRA DURA no topo).
- Barras do zero, rotuladas, todas começando no mesmo ponto (rótulo com largura fixa, `flex-shrink:0`); comparar igual com igual (nunca duas fontes diferentes no mesmo gráfico); dizer quando a conta mudou (asterisco). Ano sem dado publicado = barra tracejada "AINDA NÃO PUBLICADO", nunca estimativa nossa.
- Comparação de frequência: mesmo período e mesmo lugar dos dois lados (ex.: crimes na saída de 11 dias em SP × roubos em SP nos mesmos 11 dias); nunca misturar um número de um evento com um total anual.
- Nunca "vote X". Veredito sobre a afirmação, não a pessoa.
- Texto tem que funcionar no mudo; nome da página pequeno embaixo sempre.
- Rostos: foto real, só a cabeça, recortada com contorno branco grosso. Sempre dá pra achar foto (Wikimedia, Agência Brasil, Câmara, Senado); ela não aceita círculo com iniciais nem caixa vazia. Sem recorte de cabeça quando o clipe da própria pessoa já está na tela. Não usar recorte de outra página na versão final.
- Som: trilha + SFX sintetizados — sério, sem música de comédia.
- Legenda do post: começa com COMPARTILHA NOS STORIES + Melhores Amigos; não nomear o presidente na legenda/hashtags; nada de nome de político em hashtag; crédito à página de referência SÓ com aprovação dela (perguntar antes; nunca creditar quem espalha a desinformação checada). Modelo do reel de SP: pergunta-tese, "fomos aos dados… dos dois lados", 4 ✔️ com achados dos dois lados, frase-princípio ("quem governa leva o crédito do que melhora e a conta do que piora"), pergunta, "dados, metodologia e fontes completas no primeiro comentário", 5 hashtags. 1º comentário: COMENTA …, linha ".", linha ".", 📚 FONTES por tema e 📝 NOTAS de metodologia. Os dois vão no painel de postagem da prévia (§6a.8).
- Ao encurtar o vídeo, nunca tirar algo que ela pediu pra incluir; se algo pedido saiu, avisar e devolver.

## 5b. Regras de design (ela, 16/out/2026 — valem para todo reel)
- **Margem segura:** conteúdo 10% pra dentro das bordas (wrapper `.safe` com scale .9) E todo TEXTO dentro da ZONA SEGURA Reels + Stories (skill reel-zona-segura, 4/nov/2026): x 150-915, y 268-1680 (frase fixa do topo começa em 268; imagem, trilho e fundo podem sangrar). text_check.js acusa texto fora disso; antes do MP4, mostrar os prints com a moldura do Story e do Reel.
- **Largura = linha da timeline do topo** (ela, 19/out/2026): todo bloco da cena (título, texto, itens, tabelas, gráficos, letra miúda) vai exatamente de uma ponta à outra da linha do trilho `.rail` — dentro de `.safe`, `left:60px; width:960px` (gráficos `w=960`). Nada encolhido num canto nem terminando antes da ponta direita; se sobrar espaço, aumentar a fonte um pouco em vez de deixar vazio.
- **Legenda falada = SEMPRE 2 linhas cheias** (páginas de ~60–64 caracteres em 860 px; nunca 1 linha curta nem palavra sozinha), e só a cor amarela anda palavra por palavra seguindo a voz (tempos reais por palavra). Assim dá pra ler a frase sem esperar palavra por palavra (ela, 19/out/2026). No gerador: quebrar `data-words` em páginas por número de caracteres (ex.: `KAR_CHARS = 64` em `gen_rj.py`), quebrando em fim de frase só se a página já estiver ≥60% cheia; conferir que nenhuma página passa de 2 linhas.
- **Rodapé (ela, 20/out/2026, reel da saidinha):** legenda `.kar.karfull` mais baixa, left 110 / top ~1505 / width 860; @ (`#foot`) top ~1700; linha de FONTE top ~1745, width 860, lá embaixo na área dos comentários (ali nada cobre). Fonte sempre embaixo do @, sem colar no @. `window.VFILL` ~1500.
- **Nada encosta na legenda:** todo conteúdo da cena (inclusive letra miúda) termina ≥ ~60 px acima do topo da legenda. Se não couber, ENXUGAR o texto (mesmos fatos, frase mais curta) ou subir o bloco — nunca deixar letra pequena ir para perto ou para baixo da legenda.
- **Espaçamento uniforme e calculado:** `layout.js` com `data-flow="grupo:ordem"`, `data-ftop`, `data-gap`. Rodar `preview_kit/overlap_check.js` antes de publicar: ZERO sobreposição e nada fora da margem.
- **Poucas caixas.** Texto sobre foto = texto puro com sombra, ou caixa preta semitransparente com texto branco e detalhe amarelo.
- **Cores:** amarelo #FFD34D, vermelho #FF4A3D, branco; governo anterior = azul royal; nada de azul acinzentado. Cenas sobre mulher podem trocar o amarelo por rosa (#FF5FA8) em tudo (destaques, timeline, legenda, gráficos) e voltar ao amarelo depois.
- **Imagens:** não repetir imagem no mesmo vídeo (nem rosto); fotos com cara de Brasil, clima escuro (sombra/gradiente por cima).
- **Números** com ponto de milhar (1.571). Toda frase importante fica na tela tempo suficiente pra ler. Número grande não pode ocupar espaço que falta pro texto; letra pequena NÃO diminui (celular pequeno).
- **Presidente atual:** não escrever nem falar o nome. Usar "governo atual" / "sancionado pelo presidente" e o ícone 🦑. O anterior pode ser nomeado (Bolsonaro). Lei sancionada: dizer "sancionada pelo presidente" no fim.

## ABA "VÍDEO ORIGINAL" na prévia (vale para todos os formatos de reel, ela 23/out/2026)
Sempre que o reel parte de um vídeo de outra pessoa (link do Instagram, entrevista, fala de político), a prévia ganha uma aba "Vídeo original" com o vídeo inteiro, pra ela assistir e achar outros trechos que valham. Versão leve, feita uma vez só junto com os cortes (no mesmo lugar onde o MP4 já foi baixado, sem gastar outra rodada): `ffmpeg -i orig.mp4 -vf scale=432:768,fps=24 -c:v libx264 -preset slow -crf 32 -g 48 -pix_fmt yuv420p -c:a aac -b:a 64k -ac 1 -movflags +faststart original_leve.mp4` (cerca de 5 MB por 1:30) + pôster jpg. Publicar como arquivo do artifact (não data URI), `<video controls playsinline preload="none">`, sem transcrição nem análise extra. Ao trocar de aba, pausar a trilha da prévia e o vídeo original.

## ALINHAMENTO NO QUADRO — vale para os 3 formatos (Colagem, Timeline, Desabafos), ela 19/out/2026
- **Horizontal:** cada bloco ocupa a largura inteira da área útil, da ponta esquerda à ponta direita da linha de referência (na Colagem/Timeline = trilho `.rail` do topo: `left:60px; width:960px` dentro de `.safe`, gráficos `w=960`; no Desabafos = margem de 116 px dos dois lados). Nada encolhido num canto, nenhuma frase quebrando antes do fim da linha. O TEXTO desses blocos continua dentro da zona segura (x 150-915).
- **Vertical:** o conteúdo da tela se espalha no espaço entre o título do capítulo e a legenda, nunca tudo amontoado em cima com um buraco antes da legenda. Na Colagem/Timeline: `window.VFILL` (y limite, em coordenadas da cena) liga o `vfill` do `layout.js` — o 1º slot (título do capítulo) fica onde está, a sobra vira espaço extra igual entre os blocos seguintes e o que ainda sobrar desce o corpo, metade em cima e metade embaixo. `data-vfill="0"` desliga numa cena (ex.: cena de gancho com composição própria). Na prévia, o `mkpreview` também precisa pôr `window.VFILL`. No Desabafos: centralizar o bloco de texto no cartão e distribuir as linhas número+frase na altura do quadro.
- Cena com muito texto não tem sobra — tudo bem; o limite continua sendo terminar ≥ 60 px acima da legenda.
- Conferir antes de publicar: quadro do FIM de cada cena (tudo já entrou), checagem de sobreposição/margem zerada e mais baixo conteúdo de cada cena perto do limite (não 300 px acima dele).

## CAPA: obrigatória, feita junto com a 1ª versão (vale para os 3 formatos, ela 19/out/2026)
- A capa nasce quando a 1ª versão do vídeo fica pronta, não no fim. Já entra na prévia (imagem ao lado do player + botão **⬇ Capa** no painel de postagem) e acompanha toda republicação. Nunca postar sem capa: no Metricool vai em `videoThumbnailUrl`.
- O objetivo é CLIQUE, não opinião: um gancho que faça os dois lados quererem abrir (modelo: "Há 20 anos a culpa é da esquerda?", que o vídeo depois desmonta). Pode soar como a pergunta ou acusação que a direita faria; a capa não precisa ser a favor da esquerda nem do tema e nunca entrega o veredito.
- Planejada e personalizada por tema: rosto real de quem está em jogo (recortado, sem fundo, com brilho/cor do tema atrás), uma frase curta e um número ou data GRANDE que todo mundo enxerga no feed. Paleta escolhida pelo tema (ex.: rosa e preto para mulheres), não sempre a mesma. Tema que pega mais as mulheres: falar com elas na capa ("EI, MULHERES, E A SAIDINHA?") com foto de mulheres de costas, abraçadas, visíveis (texto em cima no escuro, as pessoas não ficam embaixo do texto).
- Sem fato errado e sem número fora de contexto: todo número da capa está no vídeo e tem fonte. Evitar palavra que derruba alcance ("estupro", "morte") na capa.
- Texto dentro da ZONA SEGURA Reels + Stories (skill reel-zona-segura: x 150-915, y 268-1680; imagem e fundo podem ir até a borda; conferir com a moldura do Story e do Reel antes do MP4) e legível na miniatura quadrada do grid (miolo central). Linhas do título no MESMO tamanho e cheias (nada de 1ª linha curta).
- Quando der, fazer 2–3 opções lado a lado numa imagem (A/B/C) e deixar ela escolher.
- Salvar em `motion/` (capa.jpg) e registrar no STORY doc.

## 5c. Títulos e textos enquadrados (ela, 18/out/2026 — NÃO PULAR)
Todo título, subtítulo e corpo de texto precisa ficar bonito no quadro, sem ela ter que pedir:
- Nunca deixar palavra sozinha numa linha, nem "linha comprida em cima + linha curta embaixo com espaço vazio do lado".
- Nenhuma palavra pode estourar a caixa nem passar da margem.
- **Texto corrido enche a linha até o fim** (ela, 19/out/2026): item, linha de tabela, corpo e letra miúda vão até o fim do filete/divisória — usar `text-wrap: pretty` (evita palavra órfã sem encurtar a linha). Nunca `text-wrap: balance` em texto corrido: quebra a frase cedo e deixa um vazio grande à direita. Se ainda sobrar linha curta, reescrever a frase (mesmo fato), não estreitar a caixa. Etiquetas que andam juntas (ex.: nome + etiqueta de ideologia, "LUCINHA (PSD DIREITA).") num `white-space:nowrap`.
- **Destaque colorido NUNCA quebra no meio** (ela, 20/out/2026: "por que isso não é uma regra?"): todo trecho com cor diferente ou faixa amarela/rosa (`.hl`, `<span style="color:…">`) dentro de título, chamada ou tarja anda inteiro. Se não couber na linha, o trecho todo desce pra próxima ("SE VOCÊ É MULHER, / **FICA ATÉ O FINAL.**", nunca "**FICA** / **ATÉ O FINAL**"). No gerador: pós-processar a página e pôr `white-space:nowrap` em todo span colorido de até ~26 caracteres dentro de `.el.h`, `.el.credit` e tarjas (spans maiores podem quebrar). Não aplicar em texto corrido de item/corpo (lá deixaria linha curta).
- **Palavra curta não fica no fim da linha:** artigo, preposição e palavras de 1 a 3 letras (o, a, de, da, pra, por, que, é, dá, já, 1ª, números de 1 ou 2 dígitos) colam na palavra seguinte com ` ` ("O JUIZ", "DÁ PRA"). Fazer no gerador, só nos nós de texto, nunca em `data-words` nem `<script>`.
- **Título não pode quebrar cedo** (ela, 20/out/2026): `text-wrap: balance` deixou "SAIDINHA: / DIREITO / OU PRÊMIO?" e "DENTRO / DA CADEIA." com espaço sobrando. O `fitHeads` do `layout.js` usa quebra comum (`text-wrap: wrap`, linha cheia antes de quebrar) e não aumenta a fonte acima da original (`fitmax` 1.0). Atenção: `text-wrap: wrap` mata o `white-space:nowrap`; pra desligar só o balance use `text-wrap-style: auto`.
- **Acento dentro da faixa amarela:** a faixa `.hl` precisa cobrir a altura toda da letra (`background-size:100% 96%` + `padding-top:.1em`); senão "FAMÍLIA", "DÁ" e "MANTÉM" perdem o acento (fica preto sobre o fundo escuro).
- Frase fixa no topo da tela (ex.: "VOCÊ SABE QUE SOLUÇÕES / REALMENTE TE PROTEGEM?"): em 2 linhas com `<br>`, dentro da margem, acima da timeline.
- Como fazer: carregar `fit.js` ANTES do `layout.js` na página do reel e na prévia. Ele (1) diminui a fonte se alguma palavra estoura; (2) tenta tirar uma linha inteira diminuindo até ~20% da fonte; (3) NÃO equilibra mais as linhas (balance quebrava cedo); quebra comum, linha cheia. `<br>` manual só quando ela pedir uma quebra específica.
- Checar: `node preview_kit/text_check.js <pagina>.html` → "ZERO problemas de texto" (margem, estouro e linhas, linha por linha) + `overlap_check.js` zerado + contact sheet 1 fps do vídeo INTEIRO (não só um quadro por cena), olhando quadro a quadro.

## 5d. Clipes reais dentro do reel
- Vídeo de imprensa entra como cartão (`.pcard` com `<video>`) sobre o fundo borrado de um quadro do próprio vídeo; horizontal = largura cheia (960), vertical = 340–520.
- Sempre duas fontes: `<source>` MP4 H.264 primeiro e WebM VP9 depois (no iPhone o WebM travava o clipe; o Chromium do Playwright cai no WebM sozinho). Pôr `?v=<timestamp>` no src pra celular não usar clipe velho do cache. Codificar com GOP curto (`-g 6`) pra busca ficar rápida.
- Sincronizar pelo áudio sem ficar buscando: buscar só quando a cena começa ou o usuário pula; depois só se desviar >0,6 s; carregar TODOS os clipes quando a página abre (`preload=auto` + `load()`); pré-carregar só 1,2 s antes congelava o clipe no celular (ela, 20/out/2026). Buscar a cada quadro = clipe travado. No modo de captura (`__exact`), buscar só se desviar >0,02 s e ESPERAR o `seeked` de cada clipe visível antes do print (`tools/capture_exact.js` da saidinha; dá pra renderizar em 4 pedaços em paralelo e juntar).
- Clipe de político: buscar a fonte oficial sem corte (canal da emissora); nunca usar corte de página de oposição, que corta nas piores partes. Tirar muletas que ela apontar ("é que", "que" sobrando) cortando pelos tempos por palavra do faster-whisper.
- Tarja por cima do clipe (ex.: "TÁ NA LEI DESDE 1984") fica no TOPO do cartão, nunca na boca da pessoa.
- Cortar o clipe no momento em que a pessoa aparece (conferir com quadros a cada 0,5 s antes de cortar), sem as cenas de violência explícita; o áudio original do clipe entra na mixagem no lugar da narração, com legenda PT por cima.

## 5e. Gráficos que acompanham a voz (reel do Rio, 19/out/2026)
- Gráfico parado com a voz falando por cima = ninguém acompanha. Tudo o que a voz cita é APONTADO no gráfico no momento em que é dito, como professor em sala: faixa amarela translúcida no período (`bands`), ponto pulsando na linha (`pings`), brilho que percorre a linha citada na cor dela (`glow`), marquinha vertical com rótulo no ano de uma medida/lei (`vmarks`, ex.: ESTATUTO DO DESARMAMENTO, UPPs, INTERVENÇÃO FEDERAL). Implementado em `preview_kit/gen_rj.py` (`segchart` e `chart`).
- Linhas entram quando o nome é dito (uma por vez; dois mandatos da mesma pessoa entram juntos, 2º mandato tracejado na mesma cor). Depois que tudo apareceu, o gráfico fica ≥ 3 s na tela antes de trocar de cena. Gráfico de comparação ("quem fez o quê") pode entrar logo no começo da cena, pra dar tempo de analisar.
- Sempre que fizer sentido, a linha do Brasil junto (cinza tracejado), na mesma escala, para mostrar o que é do estado e o que é do país.
- Narração do gráfico enxuta: nome + número direto ("Garotinho subiu vinte e seis"), sem repetir no fim o que já foi dito; mesma quantidade de contexto para os dois lados (se não explica a alta de um, não explica a do outro).
- Legenda (chave de cores) do gráfico com quadradinho colorido (`.lg`), nunca tracinho (━/┅); tracejado explicado em texto ("TRACEJADO = 2º MANDATO"). Título de capítulo sem tracinho antes.
- Um gráfico bom que explica tudo > dois gráficos que se repetem.

## 6. Produção
1. `./setup.sh` (+ fontes Rubik/Caveat do kit) → gerar a página do reel por um script `gen` (modelo: `preview_kit/gen.py`), cenas `<section class="scene" data-s data-e data-in>`, conteúdo dentro de `.safe`, `window.DUR` (e `window.VFILL`) no fim; motor = engine.js + fx.js + fx2.js + fit.js + layout.js.
2. `PAGE=<pagina>.html node snap.js snaps <tempos>` → contact sheet; `node preview_kit/overlap_check.js <pagina>.html` e `node preview_kit/text_check.js <pagina>.html` → zero linhas.
3. **PRÉVIA AO VIVO (§6a) — obrigatória antes de qualquer MP4.**
4. Só depois que ela APROVAR a prévia: `node capture.js video_noaudio.mp4 <pagina>.html` → mix (`preview_kit/mix2.py`) → ffmpeg mux (crf 23, <30 MB para o chat).
5. QA: contact sheet 1 fps do final; LUFS ~−16; duração; todo número com fonte; nenhum @ de quem espalha desinformação em tela, legenda ou 1º comentário.
6. Subir MP4 em motion/ (`GOOGLEDRIVE_UPLOAD_FROM_URL` a partir de um branch temporário, ou OAuth Python no Mac, sempre supportsAllDrives); STORY doc com Composio GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN → mover para a pasta; revisões com append. Nunca create_file com conteúdo. No runner do GitHub (setup-python 3.11), f-string com a mesma aspa dentro quebra: rodar geradores com `/usr/bin/python3` (3.12).
7. Agendar no Metricool (ver §7).

## 6a. Prévia ao vivo (artifact) — ANTES de renderizar qualquer MP4
Ler `preview_kit/README.md` primeiro. Modelo aprovado por ela: https://claude.ai/artifact/GFQ8SVUf8NmyEb5UNz2VVN ("Querida amiga"). A prévia é publicada com a ferramenta Artifact e precisa ter:
1. O vídeo inteiro rodando no navegador, em tamanho de celular, sem cortar: palco 1080×1920 dentro de `#scaler` escalado (NUNCA escalar `#stage`, o shake sobrescreve), largura ≤ 520 px, tema escuro.
2. Narração sincronizada usando o áudio como relógio (`render(audio.currentTime)` — `mkpreview.py` troca o loop do engine.js); `narracao.mp3?v=<timestamp>` para não pegar cache velho.
3. Controles: ▶ Play/❚❚ Pausa (`play()` com catch: recarrega o áudio e tenta de novo), barra de busca com `m:ss / total`, botões **↺30s ↺10s ↺5s 5s↻ 10s↻ 30s↻**, velocidades **1x · 1,05x · 1,1x · 1,2x · 1,5x · 2x · 3x** (`playbackRate`, `preservesPitch`), teclado ← → pula 5 s (Shift = 10 s), espaço = play/pausa.
   - **Caixa de anotações (obrigatória em toda prévia):** logo abaixo das velocidades, uma caixa "Suas anotações" (textarea) para ela digitar enquanto assiste, com botão **+ Marcar tempo** (insere `[m:ss]` do ponto atual do player) e botão **Copiar** (para colar na conversa). A caixa cresce até ~260 px e depois rola por dentro (`max-height` + `overflow-y:auto`, `resize:vertical`, `box-sizing:border-box`, largura 100%); nunca empurra a página nem cria rolagem lateral. Texto guardado no navegador (localStorage com try/catch, uma chave por reel) para não sumir se a página recarregar.
   - **Aba "Vídeo original"** quando o reel parte de um vídeo de outra pessoa (ver seção própria).
4. Arquivos ao lado da página (assets/, fontes, fotos, vídeos, `narracao.mp3`, js/css incluindo `fit.js` e o `layout.js` atual) publicados via `files`.
5. Antes de cada publicação: `overlap_check.js` e `text_check.js` zerados + contact sheet 1 fps do vídeo inteiro, olhando os quadros. Depois de gerar a página, rodar `karpage.js` (legenda em 2 linhas) e `karcheck.js` (zero páginas fora de 2 linhas).
6. A cada rodada de ajuste: republicar no MESMO link (mesmo file_path), `label` curto, e dizer a ela em 1 frase o que mudou. Duração máxima que ela definir (ex.: 2:30) vale também aqui.
7. Só renderizar o MP4 quando ela aprovar a prévia → SendUserFile no chat → Drive `motion/` → NOTE datada no STORY doc.
8. **Painel de postagem (obrigatório em toda prévia):** embaixo do player, `preview_kit/post_panel.py` (`add_panel(page, OUT, pasta_do_reel)`) põe: botão **⬇ Vídeo MP4** (aparece quando existir `video.mp4`; antes disso mostra "MP4 sai após aprovação") e **⬇ Roteiro**, e campos com botão **Copiar** para **Legenda do post**, **Primeiro comentário** e **Prompt pra checagem (ChatGPT)**. Os textos vêm de `data/<slug>/post/legenda.txt`, `primeiro_comentario.txt` e `prompt_chatgpt.txt`. A capa (ver CAPA) aparece no painel com botão **⬇ Capa** desde a 1ª versão. Download só funciona pela capability: publicar com `capabilities: {"downloads": true}` (MP3 não está na lista de extensões permitidas; MP4/TXT sim).
9. **Prompt pra checagem no ChatGPT:** o mesmo do skill reel-pasta-roteiro-auditoria (passo 3, que inclui a avaliação do fio da história), com o roteiro completo (FALA + NA TELA por cena) e estes avisos a mais: só checar fatos; não procurar argumento pra defender nenhum lado nem sugerir "outro lado"; responder SÓ o que estiver errado (frase, erro, dado correto, fonte com link), nunca listar o que está certo; "governo atual" + 🦑 é proposital; ideologia segue Bolognesi et al. (2023).
Vale também para Timeline e Desabafos (sem narração: mp3 silencioso com a duração do vídeo como relógio).

## 7. Agendamento e COLABORADORES (ela, 20/out/2026 — vale para todo post político da página)
- Marca no Metricool: **tentandochegaratevoce** (`blogId 7092974`, fuso America/New_York). Reel = `instagramData.type: "REEL"`, capa em `videoThumbnailUrl`, 1º comentário em `firstCommentText`. Essa marca só tem Instagram e TikTok conectados (sem Facebook).
- **Colaboradores padrão (convite de collab no Instagram):** `brasilforadacaverna` (Brasil fora da caverna — sempre convidar), `designativista` (Design Ativista), `342artes` (Movimento 342 Artes), `ojorgevinicio` (Jorge Vinicio), e **Seu voto decide** (pedir o @ exato a ela até estar confirmado aqui; nunca chutar @). **No máximo 3 colaboradores por post**: com 5 o Instagram falhou ("Media container not created"), com 1 a 3 publica.
- Em `instagramData.collaborators: [{"username": "...", "deleted": false}]`. Conferir cada @ antes (ela: "tomar cuidado para não colocar errado"). Nunca convidar, marcar ou citar o @ de quem espalha a desinformação checada.
- **Comportamento:** já colocar a lista padrão no agendamento e AVISAR na mesma mensagem: "convidei @a, @b, @c — mantém ou tira algum?". Se ela pedir pra perguntar antes, perguntar "quer que convide esses?" e só então agendar. Quando ela mandar um post já agendado de outro chat, adicionar a mesma lista nele também (`updateScheduledPost` com o post inteiro, só trocando os colaboradores).
- Sempre entregar a lista em texto pronto pra copiar ("@brasilforadacaverna @designativista @342artes @ojorgevinicio"), pra ela mandar em outro chat.
- Intervalo entre posts da página: ~3–4 h (ela agenda uns às ~14h30 e outros às ~17h ET).
- **Trial reel** do mesmo vídeo (`instagramData.type: "TRIAL_REEL"`, `shareTrialAutomatically: false`): sempre com legenda e 1º comentário reescritos (mesmos fatos, texto diferente), pro Instagram não tratar como o mesmo post.