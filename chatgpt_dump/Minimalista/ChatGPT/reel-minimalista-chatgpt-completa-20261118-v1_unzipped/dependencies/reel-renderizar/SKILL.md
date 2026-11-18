---
name: "reel-renderizar"
description: "Render the approved reel preview to MP4, check it, and prepare the posting package (comments, collabs, public media for Metricool)."
---

# Renderizar e preparar pra postar (todos os skills de reel)

Vale pra todo reel feito como prévia HTML (motion, colagem, pontilhado, timeline, placar, desabafos, 3D, split, OPC, quem-tem-culpa). O skill de formato continua mandando no visual; este skill manda no "renderiza". Não pesquisar caminho de render de novo: seguir este.

## Destino no Drive decidido antes do render (15/nov/2026)
Antes de renderizar, confirmar como o MP4 chega na pasta do Drive: Mac conectado = gravar direto na pasta sincronizada do Google Drive para desktop; só nuvem = avisar já que ela vai salvar pelo cartão (o conector do Drive não sobe vídeo grande). Nunca descobrir isso só depois do render. Se fugir do Drive, explicar o porquê.

## 0. Antes de começar (2 minutos)
1. Pegar a versão VIVA da prévia (list_files + read_file). Se outra conversa publicou depois, montar em cima dela, nunca por cima.
2. Checagem final rápida, sem ela pedir:
   - Dados que mudam (placar de consulta, contagem de votos, preço) atualizados no dia. Se mudou, atualizar a tela antes do render.
   - Toda pessoa na tela com cabeça recortada + chip partido · ideologia. Nada do nome do presidente atual.
   - Legenda falada sempre em 2 linhas, sem palavra sozinha.
   - Zona segura (reel-zona-segura) e som (reel-som) ok.
3. Avisar numa linha quanto tempo o render deve levar.

## 1. Render (o caminho rápido, 08/nov/2026: 3:33 de vídeo em ~5 min)
No container local:
1. Copiar pra uma pasta local TODOS os arquivos da prévia (index.html, data.js, fontes, heads/, imagens, scripts 3D, three.module.min.js). Faltou fonte ou imagem = render errado.
2. Servir com `python3 -m http.server 8765` (módulos ES e fontes não carregam por file://).
3. Playwright Chromium com `--use-gl=swiftshader --enable-webgl --ignore-gpu-blocklist` (3D funciona), viewport 1080x1920. Fixar o #frame em 1080x1920 sem escala.
4. Congelar o loop (`window.__freeze=true`) e, a cada quadro, chamar uma função de passo que:
   - chama `render(t)` da prévia;
   - pega `document.getAnimations()`, marca o instante em que cada animação apareceu (`an.__t0 = t` na primeira vez), dá `pause()` e põe `currentTime = (t − __t0) × 1000`.
   Assim as transições CSS seguem o relógio do vídeo, não o relógio real.
5. Clipes de vídeo na tela: extrair os quadros antes (`ffmpeg -i clip.mp4 -q:v 3 fr/%05d.jpg`) e trocar o `<video>` por `<img>` no render (lição do reel-pontilhado-cinetico). Nunca buscar `video.currentTime` quadro a quadro.
6. Screenshot em JPEG qualidade 92 direto num pipe pro ffmpeg (`-f image2pipe -vcodec mjpeg`, x264 `-preset veryfast -crf 18`), 30 qps.
7. Dividir em pedaços iguais, um processo por núcleo (`nproc`), rodando em segundo plano. Juntar com `concat` e colocar o áudio aprovado (o fundo padrão do play) com AAC 192k, `-crf 21`, `+faststart`.
8. Nunca baixar qualidade ou qps pra ganhar tempo sem perguntar.

## 1b. Carrossel animado (cada card vira um MP4)
- Card 1 é a capa: gravar começando DEPOIS que todas as entradas terminaram (ex.: ffmpeg -ss 4.5), pra o quadro 0 já ter tudo. Conferir com print do quadro 0.
- Cards 2+ gravam do começo, com as revelações.
- Arquivo grande demais pro conector (~3 MB): subir card a card, não o vídeo juntado.

## 2. Conferir antes de mostrar
- Duração do MP4 = duração do áudio.
- Tirar ~20 quadros espalhados (um por cena e nos momentos de animação) e olhar em grade: imagem faltando, texto cortado, sobreposição, 3D preto, cabeça sem foto. Corrigir e re-renderizar só o pedaço afetado.

## 3. Entregar pra ela assistir (ela sempre assiste uma vez antes de postar)
- SendUserFile com o MP4 em qualidade cheia.
- Na prévia: player `<video>` com uma cópia leve (artifact aceita até 20 MiB por arquivo) e botões de baixar vídeo e capa pela capability `downloads` (declarar `downloads:true` antes; `.mp3` não é aceito no download, só mp4/jpg/png etc.).

## 4. Pacote de postagem, montado enquanto renderiza e mostrado no chat
1. **Legenda** (regras da marca: COMPARTILHA NOS STORIES no começo, sem nome do presidente).
2. **1º comentário (o Claude posta e fixa):** chamada pra comentar, linhas com ".", e as ações numeradas com LINKS DIRETOS das páginas oficiais. Nunca encurtador (bit.ly): ela não paga e dá propaganda. Explicar o que fazer em cada link ("escolhe tal órgão", "coloca esses em cópia no mesmo e-mail"). Quando tiver como cobrar alguém, dar mais de um caminho (site + e-mail).
3. **2º comentário (ela posta à mão depois):** mensagens prontas pra copiar e colar, pedido de outras petições e créditos (foto e música com autor, licença e "imagem recortada"/"trecho editado").
4. **Collabs (até 5) e marcações (sem ser collab):** consultar a aba "🤝 Collabs e marcações" do News — Content Control e os prints que ela mandar; collab só quem tem cara de aliado da causa; os outros entram como marcação no reel. Trial não leva collab.
5. Mostrar tudo no chat em blocos prontos pra copiar e salvar os mesmos textos nos campos da prévia.
6. Auditoria do comentário: oferecer o prompt pro ChatGPT e revisar a resposta com cuidado (ele costuma pôr ressalva demais e defender o outro lado).

## 5. Metricool (é o Claude que posta)
1. A mídia precisa de link público. Caminho padrão, SEM perguntar a ela (já autorizado pra sempre): cópia do MP4 e da capa na pasta "Metricool public" do Drive (ID 1_i1tkJDOz0LNKsWOvcNnAmSmDhll2SQ3), cópia pra lixeira logo que o Metricool criar o post. O original fica na pasta privada do conteúdo. Se o MP4 só existe na nuvem do Claude: device_commit_files pro Mac (~/ClaudeWorkspace/_ugc_upload) e o Finder copia pra pasta sincronizada do Drive (~/Library/CloudStorage/GoogleDrive-priscila@oakpark-construction.com/Shared drives/...). O GitHub abaixo é só reserva enquanto o repo ainda for público.
2. CAMINHO QUE FUNCIONA (testado 11/nov/2026, reel Vota aí), sem pedir nada a ela e sem Mac:
   a. `add_repo` priihigashi/oak-park-ai-hub com access "push" (não precisa clonar).
   b. No container: `git init` numa pasta nova, `git checkout --orphan tmp-<slug>-media`, copiar só o MP4 e a capa, commit, `git remote add origin https://github.com/priihigashi/oak-park-ai-hub`, `git push origin tmp-<slug>-media`. O main é protegido; branch órfão sobe só os arquivos.
   c. Link público: https://raw.githubusercontent.com/priihigashi/oak-park-ai-hub/tmp-<slug>-media/<arquivo>. Passar direto no `media` e no `videoThumbnailUrl` do Metricool (ele copia pro static.metricool.com na hora).
   d. Logo depois de criar os posts, apagar o branch pelo Workbench do Composio: proxy_execute DELETE /repos/priihigashi/oak-park-ai-hub/git/refs/heads/tmp-<slug>-media (o `git push --delete` pelo proxy do container cai). Confirmar com GET (404).
   - Arquivo no sentido contrário (gerado no Workbench, ex. voz edge-tts, que não roda no container): PUT /contents num branch temporário pelo proxy_execute do Workbench, baixar no container pelo raw, apagar o branch.
   - NÃO funciona: create_file do Drive com referência de arquivo do container; download do S3/R2 do Composio no container.
3. Criar o post SEM horário ou como rascunho até ela dizer que assistiu e aprovou. Quando ela pedir "posta" (e "nos stories também"): Reel em instagram+facebook+tiktok com capa e 1º comentário, e um segundo post STORY em instagram+facebook uns 3 min depois (avisar que o adesivo de link do story ela põe à mão). Depois seguir postar-agendar (prazo de validade, trials, repost) e, publicado, reel-fechamento.

## 6. Resposta pra ela
Curta: o vídeo pra assistir, o que conferiu, os blocos de texto, collabs e marcações, e o que falta (ex.: aprovação dela pra postar).