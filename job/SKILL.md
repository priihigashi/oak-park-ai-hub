---
name: "reel-placar-checagem"
description: "Reel de checagem de entrevista ou debate de político com placar FAKE / MEIO TERMO / VERDADE: vídeo em cima, placar no meio (um por pessoa em debate), fato e fonte embaixo; pausa a cada frase."
---

# Reel Placar da Checagem

Formato aprovado pela Priih em 24/out/2026 no reel "Flávio na entrevista: 8 frases, 1 placar" (versão final: Drive › News › Brazil › Reels_Shorts › v3_placar-flavio-desmatamento). É um nicho do `reel-pontilhado-cinetico`: mesma textura de pontinhos, fontes, legenda e regras de voz. Layout revisado em 24/out/2026 (reel da marcação das balas) depois de ver o post no ar: o topo ficava embaixo do cabeçalho da collab e sobrava espaço embaixo. Kit de código (template.html, scenes.py de exemplo, build.py, make_page.py, audit.py, render.py, recut.py, job/run.py e workflow): Drive › Tools, Skills & Flows › Skills › reel-placar-checagem › `reel-placar-checagem_kit.zip`. Baixar o kit e partir dele; só trocar scenes.py, clips.json e o texto.

Quando usar: ela manda o link de uma entrevista, fala ou debate de político e pede "placar", "true or false", "faz igual ao do Flávio".

## Dois modos
- **Modo entrevista (1 pessoa):** um placar só, como no reel do Flávio.
- **Modo debate (2 pessoas):** sempre que houver frases checadas de duas pessoas (debate, entrevista com resposta do adversário), cada uma tem o SEU placar. Nunca somar as duas pessoas num placar só: o público quer saber quem errou mais. Ver "Placar duplo" abaixo.

## Zonas do Instagram (no palco 1080x1920)
- Topo y 0 a 160: cabeçalho do post (nome da conta, collab, "áudio original", menu). Nada importante ali.
- Direita x > 960, y 1050 a 1565: botões (curtir, comentar, enviar). Legenda e painel nunca entram ali.
- Base y > 1565: caixa de comentário / descrição / balão de reação (esquerda, y 1565 a 1760), meio transparente e às vezes some. Só o @ e a linha de fonte ficam aqui; a legenda falada termina antes de y 1565.

## Layout FIXO (palco 1080x1920, igualzinho em todo vídeo)
Margem lateral 108 px (x 108 a 972). Tudo desce pra fugir do cabeçalho e ocupa o espaço até o @, sem buraco embaixo. Alturas não mudam de vídeo pra vídeo.

| Bloco | Posição | Detalhe |
|---|---|---|
| Faixa do topo | y 170 | etiqueta "CHECAGEM" (Figtree 800 30px) à esquerda; "Entrevista · mês/ano" ou "Debate · mês/ano" à direita. Nunca o nome da emissora. |
| Caixinha do vídeo | y 226, 864x540 | cantos 30 px, contorno preto deslocado 10 px que treme de leve. Vídeo 768x480 com laterais desfocadas (ver Vídeo dele). |
| Chip de quem fala | canto inferior esquerdo da caixa, sai 30 px | nome · partido · ideologia (azul direita / vermelho esquerda). Repórter/mediador = chip branco com texto preto fixo #141416 (nunca var(--ink), que some no fundo preto). Na narração o chip é de quem aparece congelado (último clipe; na abertura, o primeiro clipe). |
| Pausa | dentro da caixa, canto sup. esquerdo | badge preto "Pausa pra checar" + vídeo congela no último quadro em cinza. |
| Placar | y 822 | modo entrevista: "Provavelmente:" pequeno cinza (proteção jurídica) + 3 caixas iguais: FAKE vermelho #FF4A3D, MEIO TERMO amarelo (texto #C99400), VERDADE verde #1FAF5A, número 64px. Ao marcar ponto a caixa pisca na cor e pula. Modo debate: ver "Placar duplo". |
| Painel de comentários | y 976 a 1410 | ver abaixo |
| Legenda falada | y 1436, x 108 a 930 (longe dos botões do Instagram) | Figtree 800 52px, 2 linhas por página, máx 26 caracteres por linha, palavra atual fundo preto + texto amarelo. Termina em y ~1560, logo acima do balão de reação; fica perto do @. |
| @tentandochegaratevoce | y 1650 | já na área do comentário, de propósito |
| Fonte | y 1694 | 22px, muda a cada cena |

### Placar duplo (modo debate)
Ocupa a mesma faixa do placar simples (y 822 até cerca de 966), sem empurrar o painel.
- "Provavelmente:" pequeno cinza em cima, centralizado.
- Duas metades lado a lado (x 108 a 528 e x 552 a 972), separadas por um "x" pequeno no meio.
- Cada metade: cabeça recortada pequena (só cabeça, contorno branco, cerca de 72 px) + nome curto + bolinha da ideologia (azul direita / vermelho esquerda) numa linha; embaixo, 3 caixinhas F / MT / V nas cores do placar, número 44px, todas da mesma altura.
- Quem está sendo checado fica em destaque (contorno preto grosso, opacidade 1); a outra metade fica em 55% de opacidade. Ao marcar ponto, só a caixinha da pessoa checada pisca e pula.
- Ordem fixa no vídeo inteiro: esquerda = quem falou primeiro no debate. Nunca trocar de lado no meio.
- O carimbo do painel continua igual; a frase "ELE DISSE" vira "FLÁVIO DISSE" / "[nome] DISSE" (presidente atual: "GOVERNO ATUAL DISSE" + lula desenhada, nunca o nome).
- Final do modo debate: dois blocos grandes, um por pessoa (cabeça + chip + F/MT/V), lado a lado ou um em cima do outro, com os números começando na mesma altura. Embaixo, uma frase neutra lendo o resultado ("Dos dois, quem mais errou nesta seleção de frases foi..." só se a diferença for clara; empate = dizer empate). Lembrar em letra miúda que o placar vale para as frases escolhidas, não para o debate todo.
- Equilíbrio: escolher frases checáveis dos dois lados com a mesma régua. Não forçar número igual de frases nem de fakes; não balancear artificialmente.

### Painel de comentários (cada frase checada)
1. "ELE DISSE" (ou "[nome] DISSE" no modo debate) + afirmação entre aspas em Figtree 700 35px preta com barrinha da cor do tema; padding-right 425px pra nunca passar por baixo do carimbo.
2. Carimbo no canto superior direito: "Provavelmente" + FAKE / MEIO TERMO / VERDADE (900 48px), torto, cai com slam na palavra do veredito. Dois vereditos na mesma frase: o segundo cobre o primeiro.
3. Provas (1 a 3): número grande + rótulo (.row 78px); 3 números lado a lado (.tiles, mesma altura); checks ✓/✗; barras comparando governos (azul royal #2D55D6 = anterior/direita, vermelho = atual); gráfico de colunas ano a ano (.chart, barras crescem uma depois da outra, período de direita com fundo azul clarinho e linhas tracejadas).
4. Letra miúda no rodapé do painel (24px), nunca abaixo de y 1422.
- Elementos com flex-shrink 0, painel space-between (espalha até o fim do painel).
- Pessoa citada no painel: cabeça recortada + chip nome · partido · ideologia.
- Cena do clipe: painel mostra o contexto ("PERGUNTA DA REPÓRTER" ou "PERGUNTA DO MEDIADOR" + pergunta em serifa itálica 54px + data da entrevista ou do debate), centralizado.
- Abertura: "Verdadeiro" + "ou falso?" com marca-texto, depois "Vamos verificar essa entrevista." (ou "esse debate") em serifa itálica. Sem cabeça recortada.
- Final: 3 cartões grandes com o placar final (ou o final do modo debate) + CTA do dia + "Manda pra quem ainda tá na dúvida."

## Fundo em rotação
`data-bg` no #stage (variável BG no make_page.py): branco (padrão), preto, vermelho, amarelo, verde, rosa, laranja, lilas. Pontinhos e grão em todos. Em fundo colorido o gráfico ganha placa branca, o marca-texto vira branco e a legenda continua preta/amarela. Conteúdo político: evitar azul e coral de fundo. Alternar a cada vídeo da série.

## Régua do veredito (mesma para os dois lados)
- Julgar o que a frase faz o público concluir, não só o número. Pôr culpa no adversário por algo que começou antes (ou pegar mérito de outro governo) = FAKE quando isso é o centro da frase.
- Se o centro da frase é mentira, é FAKE mesmo que também falte contexto. MEIO TERMO é para frase com base real que exagera, subestima ou omite.
- Direção do erro: número errado contra o próprio argumento não é FAKE (a mensagem dele fica até mais forte). Número inflado a favor de quem fala: grande ou que muda o sentido = FAKE; pequeno = MEIO TERMO. Não exigir número exato quando a aproximação é razoável.
- Não endurecer por endurecer nem rebaixar para equilibrar os lados.
- Violência contra a mulher: nunca minimizar.
- O que não dá para verificar: cortar fora, nem mencionar.

## Roteiro
- Abertura curta, de 3 segundos: "Verdadeiro ou falso? Vamos verificar essa entrevista." (no debate: "esse debate") e já entra o clipe da pergunta. Nada de resumir as falas antes do clipe.
- Explicação de contexto ("pra entender a pergunta...") vem logo depois do primeiro clipe, curta.
- Por frase: clipe curto dele → pausa → veredito na primeira frase da narração → prova com número + comparação com o governo anterior (melhor com melhor, pior com pior) → próximo clipe.
- Nunca afirmar por conta própria: "segundo o Inpe", "os dados mostram". Selo sempre "Provavelmente".
- Crédito explícito quando ele acertar. Meio termo = dizer a parte certa e a que não bate.
- Dizer de quem é a responsabilidade (estado x federal) sempre que der.
- Fechar com placar falado (no debate, o de cada um) + CTA + "fontes no primeiro comentário". Conferir que o placar falado bate com os carimbos.

## Vídeo dele
- Baixar pelo resource_downloader.yml ou capture_pipeline.yml (transcribe_only); o MP4 fica na pasta da captura no Drive.
- No GitHub Actions (branch tmp-<slug>, workflow do kit): baixar do Drive com SHEETS_TOKEN, gerar work.mp4 e original_leve.mp4, transcrever com faster-whisper medium por palavra.
- Enquadramento: antes de cortar, fazer uma folha de quadros (um a cada 0,5 s em cada clipe) e conferir que a cabeça inteira aparece em todos os planos (close e câmera aberta). Vídeo vertical: recorte 540x480 a partir do topo (abaixo vem o texto do repost), colocado sobre o mesmo quadro desfocado em 768x480. Nunca recortar só o rosto.
- Logos: apagar com delogo só onde aparecem. Logo que entra e sai com o plano usa `enable='between(t,a,b)'` pra não borrar a cabeça de ninguém nos outros planos. Não citar o nome da emissora em lugar nenhum (Meta derruba). Só "entrevista" ou "debate".
- Clipes a 1,2x (setpts=PTS/1.2 + atempo=1.2), áudio com highpass + compressor + loudnorm -15.
- Corrigir erros do Whisper na legenda (FIX no scenes.py). Nome do presidente atual falado no clipe vira "[governo atual]" na legenda.

## Voz
- Rascunho: Microsoft grátis pt-BR-ThalitaNeural, rate +30%, pelo workflow. Nunca a ThalitaMultilingual (sai com sotaque espanhol).
- Final aprovado: ElevenLabs Mark (UgBBYS2sOqTuMpoF3BR0, eleven_v3), 1 take por cena, generations_count 1. Custo do Flávio: ~2.100 créditos.
- Workflow baixa o content_url, corta silêncio das pontas, atempo=1.2, transcreve e o build.py alinha ao roteiro (difflib).
- MP4 final acelerado mais 1,1x (setpts=PTS/1.1 + atempo=1.1). Já sair assim.

## Prévia, auditoria e render
- Prévia (artifact): a prévia que ela assiste é um MP4 renderizado (render.py, 720x1280), não o HTML ao vivo: no celular o vídeo do HTML trava. `MP4=preview.mp4` no make_page.py liga o modo MP4 do template (mesmos botões ↺30/10/5 e 5/10/30↻, velocidades 1 a 3x, caixa de notas). Renderizar sem MP4 e depois gerar a página com MP4. Abas "Vídeo original" (logo apagado) e "Capa e legenda" com campos de copiar.
- audit.py: todos os gatilhos e páginas de legenda; nada fora de x 100–995, painel até 1422, nada sobreposto, nenhuma legenda com 3 linhas. No modo debate, conferir também que as duas metades do placar não se encostam e que os números começam na mesma altura.
- Antes de entregar: print do último quadro de cada card do MP4 com as zonas do Instagram marcadas (topo y<160; direita x>960 y 1050–1565; base y>1565) e conferir um por um.
- Render: render.py (Playwright quadro a quadro, quadros do clipe extraídos em fr/*.jpg, renderAt(t)), 2 processos em paralelo (3 trava a máquina de 2 núcleos). ~13 min para 3 min de vídeo. Nunca pkill -f com padrão que case com o próprio shell.

## Post
- Capa: cabeça dele recortada (só cabeça, contorno branco) + "Fulano na entrevista: N frases, 1 placar" + placar com "?" nas 3 cores. No debate: as duas cabeças com "x" no meio + "N frases, 2 placares" + dois placares com "?". Nunca o resultado na capa.
- Legenda imparcial curta (começa com "COMPARTILHA NOS STORIES", sem nome do presidente, hashtags só de tema), 1º comentário com COMENTA + fontes mais confiáveis.
- Pasta: News › Brazil › Reels_Shorts › v<N>_<slug>/ (motion, png, resources) + cópia na Metricool public. Agendar no Metricool (IG Reel + FB Reel + TikTok) com collabs.
- Véspera de eleição: nunca agendar conteúdo político novo para o dia da votação (Lei 9.504, art. 39 §5º IV).