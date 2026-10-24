---
name: reel-placar-checagem
description: Reel de checagem de entrevista de político com placar FAKE / MEIO TERMO / VERDADE: vídeo em cima, placar no meio, fato e fonte embaixo; pausa a cada frase.
---

# Reel Placar da Checagem

Formato aprovado pela Priih em 24/out/2026 no reel "Flávio na entrevista: 8 frases, 1 placar" (versão final: Drive › News › Brazil › Reels_Shorts › v3_placar-flavio-desmatamento). Layout revisado em 24/out/2026 (reel da marcação das balas) depois de ver o post no ar: o topo ficava embaixo do cabeçalho da collab e sobrava espaço embaixo. É um nicho do `reel-pontilhado-cinetico`: mesma textura de pontinhos, fontes, legenda e regras de voz. Kit de código (template.html, scenes.py de exemplo, build.py, make_page.py, audit.py, render.py, recut.py, job/run.py e workflow): Drive › Tools, Skills & Flows › Skills › reel-placar-checagem › `reel-placar-checagem_kit.zip`. Baixar o kit e partir dele; só trocar scenes.py, clips.json e o texto.

Quando usar: ela manda o link de uma entrevista/fala de político e pede "placar", "true or false", "faz igual ao do Flávio".

## Zonas do Instagram (no palco 1080x1920)
- Topo y 0 a 160: cabeçalho do post (nome da conta, collab, "áudio original", menu). Nada importante ali.
- Direita x > 960, y 1050 a 1600: botões (curtir, comentar, enviar). Legenda e painel nunca entram ali.
- Base y > 1600: caixa de comentário / descrição, meio transparente e às vezes some. Só o @ e a linha de fonte ficam aqui.
- Esquerda x < 210, y 1540 a 1660: balãozinho de reação nos stories. A legenda termina acima disso ou fica centralizada sem encostar na esquerda.

## Layout FIXO (palco 1080x1920, igualzinho em todo vídeo)
Margem lateral 108 px (x 108 a 972). Tudo desce pra fugir do cabeçalho e ocupa o espaço até o @, sem buraco embaixo.

| Bloco | Posição | Detalhe |
|---|---|---|
| Faixa do topo | y 176 | etiqueta "CHECAGEM" (Figtree 800 30px) à esquerda; "Entrevista · mês/ano" à direita. Nunca o nome da emissora. |
| Caixinha do vídeo | y 236, 864x540 | cantos 30 px, contorno preto deslocado 10 px que treme de leve. Vídeo 768x480 com laterais desfocadas (ver Vídeo dele). |
| Chip de quem fala | canto inferior esquerdo da caixa, sai 30 px | nome · partido · ideologia (azul direita / vermelho esquerda). Repórter = chip branco "Repórter" com texto preto fixo #141416 (nunca var(--ink), que some no fundo preto). |
| Pausa | dentro da caixa, canto sup. esquerdo | badge preto "Pausa pra checar" + vídeo congela no último quadro em cinza. |
| Placar | y 840 | "Provavelmente:" pequeno cinza (proteção jurídica) + 3 caixas iguais: FAKE vermelho #FF4A3D, MEIO TERMO amarelo (texto #C99400), VERDADE verde #1FAF5A, número 64px. Ao marcar ponto a caixa pisca na cor e pula. |
| Painel de comentários | y 1000 a 1460 | ver abaixo |
| Legenda falada | y 1500, x 108 a 930 | Figtree 800 52px, 2 linhas por página, máx 26 caracteres por linha, palavra atual fundo preto + texto amarelo. Fica perto do @. |
| @tentandochegaratevoce | y 1690 | já na área do comentário, de propósito |
| Fonte | y 1734 | 22px, muda a cada cena |

### Painel de comentários (cada frase checada)
1. "ELE DISSE" + afirmação dele entre aspas em Figtree 700 35px preta com barrinha da cor do tema; padding-right 425px pra nunca passar por baixo do carimbo.
2. Carimbo no canto superior direito: "Provavelmente" + FAKE / MEIO TERMO / VERDADE (900 48px), torto, cai com slam na palavra do veredito. Dois vereditos na mesma frase: o segundo cobre o primeiro.
3. Provas (1 a 3): número grande + rótulo (.row 78px); 3 números lado a lado (.tiles, mesma altura); checks ✓/✗; barras comparando governos (azul royal #2D55D6 = anterior/direita, vermelho = atual); gráfico de colunas ano a ano (.chart, barras crescem uma depois da outra, período de direita com fundo azul clarinho e linhas tracejadas).
4. Letra miúda no rodapé do painel (24px), nunca abaixo de y 1472.
- Elementos com flex-shrink 0, painel space-between (espalha até o fim do painel).
- Cena do clipe: painel mostra o contexto ("PERGUNTA DA REPÓRTER" + pergunta em serifa itálica 54px + data da entrevista), centralizado.
- Pessoa citada no painel: cabeça recortada + chip nome · partido · ideologia.
- Final: 3 cartões grandes com o placar final + CTA do dia + "Manda pra quem ainda tá na dúvida."

## Fundo em rotação
`data-bg` no #stage (variável BG no make_page.py): branco (padrão), preto, vermelho, amarelo, verde, rosa, laranja, lilas. Pontinhos e grão em todos. Em fundo colorido o gráfico ganha placa branca, o marca-texto vira branco e a legenda continua preta/amarela. Conteúdo político: evitar azul e coral de fundo. Alternar a cada vídeo da série.

## Roteiro
- Abertura curta, de 3 segundos: "Verdadeiro ou falso? Vamos verificar essa entrevista." e já entra o clipe da pergunta. Nada de resumir as falas dele antes do clipe.
- Por frase: clipe curto dele → pausa → veredito na primeira frase da narração → prova com número + comparação com o governo anterior (melhor com melhor, pior com pior) → próximo clipe.
- Explicação de contexto ("pra entender a pergunta...") vem logo depois do primeiro clipe, curta.
- Nunca afirmar por conta própria: "segundo o Inpe", "os dados mostram". Selo sempre "Provavelmente".
- Crédito explícito quando ele acertar. Meio termo = dizer a parte certa e a que não bate.
- Dizer de quem é a responsabilidade (estado x federal) sempre que der.
- Fechar com placar falado + CTA + "fontes no primeiro comentário". Conferir que o placar falado bate com os carimbos.

## Vídeo dele
- Baixar pelo resource_downloader.yml ou capture_pipeline.yml; o MP4 fica na pasta da captura no Drive.
- No GitHub Actions (branch tmp-<slug>, workflow do kit): baixar do Drive com SHEETS_TOKEN, gerar work.mp4 e original_leve.mp4, transcrever com faster-whisper medium por palavra.
- Enquadramento: antes de cortar, fazer uma folha de quadros (um a cada 0,5 s em cada clipe) e conferir que a cabeça inteira aparece em todos os planos (close e câmera aberta). Vídeo vertical: recorte 540x480 a partir do topo (abaixo vem o texto do repost), colocado sobre o mesmo quadro desfocado em 768x480. Nunca recortar só o rosto.
- Logos: apagar com delogo só onde aparecem. Logo que entra e sai com o plano usa `enable='between(t,a,b)'` pra não borrar a cabeça de ninguém nos outros planos. Não citar o nome da emissora em lugar nenhum (Meta derruba). Só "entrevista".
- Clipes a 1,2x (setpts=PTS/1.2 + atempo=1.2), áudio com highpass + compressor + loudnorm -15.
- Corrigir erros do Whisper na legenda (FIX no scenes.py). Nome do presidente atual falado no clipe vira "[governo atual]" na legenda.

## Voz
- Rascunho: Microsoft grátis pt-BR-ThalitaNeural, rate +30%, pelo workflow. Nunca a ThalitaMultilingual (sai com sotaque espanhol).
- Final aprovado: ElevenLabs Mark (UgBBYS2sOqTuMpoF3BR0, eleven_v3), 1 take por cena, generations_count 1. Custo do Flávio: ~2.100 créditos.
- Workflow baixa o content_url, corta silêncio das pontas, atempo=1.2, transcreve e o build.py alinha ao roteiro (difflib).
- MP4 final acelerado mais 1,1x (setpts=PTS/1.1 + atempo=1.1). Já sair assim.

## Prévia, auditoria e render
- A prévia que ela assiste é um MP4 renderizado (render.py, 720x1280), não o HTML ao vivo: no celular o vídeo do HTML trava. `MP4=preview.mp4` no make_page.py liga o modo MP4 do template (mesmos botões ↺30/10/5 e 5/10/30↻, velocidades 1 a 3x, caixa de notas). Renderizar sem MP4 e depois gerar a página com MP4.
- Abas: "Vídeo original" (logo apagado) e "Capa e legenda" com campos de copiar.
- audit.py: todos os gatilhos e páginas de legenda; nada fora de x 100–995, painel até 1472, nada sobreposto, nenhuma legenda com 3 linhas.
- Antes de entregar: print do último quadro de cada card do MP4 com as zonas do Instagram marcadas (topo y<160; direita x>960 y 1050–1600; base y>1600) e conferir um por um.
- Render: render.py (Playwright quadro a quadro, quadros do clipe extraídos em fr/*.jpg, renderAt(t)), 2 processos em paralelo (3 trava a máquina de 2 núcleos). ~13 min para 3 min de vídeo. Nunca pkill -f com padrão que case com o próprio shell.

## Post
- Capa: cabeça dele recortada (só cabeça, contorno branco) + "Fulano na entrevista: N frases, 1 placar" + placar com "?" nas 3 cores. Nunca o resultado na capa.
- Legenda imparcial curta (começa com "COMPARTILHA NOS STORIES", sem nome do presidente, hashtags só de tema), 1º comentário com COMENTA + fontes mais confiáveis.
- Pasta: News › Brazil › Reels_Shorts › v<N>_<slug>/ (motion, png, resources) + cópia na Metricool public. Agendar no Metricool (IG Reel + FB Reel + TikTok) com collabs.
- Véspera de eleição: nunca agendar conteúdo político novo para o dia da votação (Lei 9.504, art. 39 §5º IV).
