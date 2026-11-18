---
name: "reel-placar-checagem"
description: "Reel de checagem de entrevista de político com placar FAKE / MEIO TERMO / VERDADE: vídeo em cima, placar no meio, fato e fonte embaixo; pausa a cada frase."
---

## Durabilidade e versão ChatGPT · 18/11/2026
Esta é uma cópia versionada para ChatGPT/Codex; o original fica em `../original/`. Antes de concluir uma alteração, preservar nova versão no Drive Creations > Tools, Skills & Flows > Skills > Reels e Carrosséis > formato > ChatGPT (usar as pastas existentes criadas por Claude) E no GitHub privado `priihigashi/news`, em branch/PR sem merge. Conferir arquivo, pasta, tamanho/hash e links nos dois destinos; registrar pendência real se algum falhar. Nunca considerar apenas o arquivo local como entrega durável; GitHub não substitui Drive. Não sobrescrever versões existentes nem alterar a versão Claude. Consultar `MANIFESTO.json` e o índice desta entrega para origem e comprovantes.

As regras atuais de `regras-priih` prevalecem sobre conflitos históricos abaixo, inclusive aprovação antes de MP4 e voz paga. Os arquivos locais citados no texto histórico não são presumidos disponíveis no celular. Dependências preservadas separadamente em `compartilhadas/`, sem fundir os formatos.


# Reel Placar da Checagem

> **Antes de roteirizar, e já no primeiro vídeo de referência:** seguir também o skill reel-pasta-roteiro-auditoria (pasta v<N>_<slug>, TRANSCRIÇÕES com cada vídeo numerado, linha no tracker com a coluna Categoria preenchida, LISTA DE FEEDBACK DA PRIIH no topo do ROTEIRO, roteiro em tabela narração | animação de cada frase, conexões entre blocos, prompt de auditoria). Ele vale junto com este skill.

Formato aprovado pela Priih em 24/out/2026 no reel "Flávio na entrevista: 8 frases, 1 placar" (versão final: Drive › News › Brazil › Reels_Shorts › v3_placar-flavio-desmatamento). Layout revisado em 24/out/2026 (reel da marcação das balas) depois de ver o post no ar: o topo ficava embaixo do cabeçalho da collab e sobrava espaço embaixo. É um nicho do `reel-pontilhado-cinetico`: mesma textura de pontinhos, fontes, legenda e regras de voz. Kit de código (template.html, scenes.py de exemplo, build.py, make_page.py, audit.py, render.py, recut.py, job/run.py e workflow): Drive › Tools, Skills & Flows › Skills › reel-placar-checagem › `reel-placar-checagem_kit.zip`. Baixar o kit e partir dele; só trocar scenes.py, clips.json e o texto.

Quando usar: ela manda o link de uma entrevista/fala de político e pede "placar", "true or false", "faz igual ao do Flávio".

## REGRA DURA: nunca o @ de quem espalha desinformação (ela, 30/out/2026)
É terminantemente proibido divulgar o @ / nome de usuário de quem está espalhando fake news. A gente não compartilha nem promove essas pessoas (não manda gente pra página dele).
- Proibido em QUALQUER lugar: linha de fonte na tela, legenda do post, 1º comentário, título do TikTok, hashtags, marcação de pessoas, convite de collab, capa e texto do story doc que vira legenda.
- Pode: nome + partido + ideologia no chip (ex.: "Nikolas Ferreira · PL · direita"), e falar "o deputado" / "o senador".
- Fonte do vídeo original fica sem @: "Vídeo do deputado no Instagram, 28/10/2026" / "Vídeo original: post do deputado no Instagram".
- Antes de agendar, procurar o @ do autor em tudo (`grep` no gerador, na legenda e no 1º comentário) e não agendar enquanto aparecer.

## Zonas do Instagram (no palco 1080x1920)
- REGRA GERAL: skill reel-zona-segura (medida em 4/nov/2026). TEXTO só em x 150-915 e y 268-1680; imagem/vídeo podem ir até a borda.
- Topo y 0 a 250: cabeçalho do Story ("@ e @collab" + tempo); no Reel aberto o zoom corta ~105 px do topo e ~52 px de cada lado. Nada importante ali.
- Direita x > 930, de y 1060 pra baixo: botões (curtir, comentar, repostar, enviar, salvar). Legenda e texto do painel nunca entram ali.
- Base y > 1685: perfil, collab, música e legenda do post. Só o @ e a linha de fonte ficam aqui (de propósito, tamanho miúdo).
- Esquerda x < 220, y 1460 a 1550: bolha "Drop an emoji" (passageira). A legenda fica entre x 190 e 915.

## Layout FIXO (palco 1080x1920, igualzinho em todo vídeo)
Caixas e vídeo podem ir de x 108 a 972; TEXTO entre x 150 e 915. Tudo desce pra fugir do cabeçalho do Story e ocupa o espaço até o @, sem buraco embaixo. (Layout revisado em 4/nov/2026 pela zona segura: testar no próximo vídeo e mostrar a ela os prints com moldura.)

| Bloco | Posição | Detalhe |
|---|---|---|
| Faixa do topo | y 268 | etiqueta "CHECAGEM" (Figtree 800 30px) à esquerda; "Entrevista · mês/ano" à direita. Nunca o nome da emissora. |
| Caixinha do vídeo | y 320, 864x486 | cantos 30 px, contorno preto deslocado 10 px que treme de leve. Vídeo 768x432 com laterais desfocadas (ver Vídeo dele). |
| Chip de quem fala | canto inferior esquerdo da caixa, sai 30 px | nome · partido · ideologia (azul direita / vermelho esquerda). Repórter = chip branco "Repórter" com texto preto fixo #141416 (nunca var(--ink), que some no fundo preto). |
| Pausa | dentro da caixa, canto sup. esquerdo | badge preto "Pausa pra checar" + vídeo congela no último quadro em cinza. |
| Placar | y 846 | "Provavelmente:" pequeno cinza (proteção jurídica) + 3 caixas iguais: FAKE vermelho #FF4A3D, MEIO TERMO amarelo (texto #C99400), VERDADE verde #1FAF5A, número 64px. Ao marcar ponto a caixa pisca na cor e pula. |
| Painel de comentários | y 1000 a 1460 | ver abaixo |
| Legenda falada | y 1490, x 190 a 915 | Figtree 800 52px, 2 linhas por página, máx 26 caracteres por linha, palavra atual fundo preto + texto amarelo. Fica perto do @. |
| @tentandochegaratevoce | y 1690 | já na área do comentário, de propósito |
| Fonte | y 1734 | 22px, muda a cada cena (nunca com o @ do autor do vídeo checado) |

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
- audit.py: todos os gatilhos e páginas de legenda; nenhum texto fora de x 150–915 / y 268–1680 (só @ e fonte embaixo), painel até 1472, nada sobreposto, nenhuma legenda com 3 linhas.
- Antes de entregar: print do último quadro de cada card do MP4 com as molduras do Story e do Reel por cima (Story: y<250 e y>1840; Reel: bordas de 52 px, topo 105, botões x>930 desde y 1060, base desde 1685) e conferir um por um.
- Render: render.py (Playwright quadro a quadro, quadros do clipe extraídos em fr/*.jpg, renderAt(t)), 2 processos em paralelo (3 trava a máquina de 2 núcleos). ~13 min para 3 min de vídeo. Nunca pkill -f com padrão que case com o próprio shell.
- No runner do GitHub (setup-python 3.11): f-string com a mesma aspa dentro (sintaxe do Python 3.12) quebra; rodar os geradores com `/usr/bin/python3` (3.12) ou não reutilizar a aspa.

## Post
- Capa: cabeça dele recortada (só cabeça, contorno branco) + "Fulano na entrevista: N frases, 1 placar" + placar com "?" nas 3 cores. Nunca o resultado na capa.
- Legenda imparcial curta (começa com "COMPARTILHA NOS STORIES", sem nome do presidente, hashtags só de tema), 1º comentário com COMENTA + fontes mais confiáveis. Nunca o @ da pessoa checada (ver REGRA DURA no topo).
- Pasta: News › Brazil › Reels_Shorts › v<N>_<slug>/ (motion, png, resources) + cópia na Metricool public. Agendar no Metricool (IG Reel + TikTok; FB só se a marca tiver Facebook conectado) com collabs: no máximo 3 colaboradores (com 5 o Instagram falhou com "Media container not created").
- Trial reel do mesmo vídeo: mudar a legenda e o 1º comentário (texto diferente, mesmos fatos) pro Instagram não tratar como o mesmo post.
- Véspera de eleição: nunca agendar conteúdo político novo para o dia da votação (Lei 9.504, art. 39 §5º IV).