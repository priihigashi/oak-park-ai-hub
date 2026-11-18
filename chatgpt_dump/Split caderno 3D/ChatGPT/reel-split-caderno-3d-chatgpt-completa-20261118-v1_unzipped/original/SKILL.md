---
name: "reel-split-caderno-3d"
description: "Reel em tela dividida estilo caderno com elementos 3D."
---

# Reel split: texto 2D em cima, história 3D embaixo

Template aprovado no reel "O Lula não criou o Fies" (FHC x Lula, postado 6/nov/2026). Em cima fica a explicação escrita (comparação, números, linha do tempo). Embaixo acontece a história em 3D (bonecos, prédios, portão, multidão). A legenda falada fica entre os dois.

Vale junto com:
- **reel-pasta-roteiro-auditoria:** pasta, ROTEIRO, TRANSCRIÇÕES, tracker e prompt de auditoria.
- **reel-3d-historinha:** stack Three.js, luz, bonecos de terno com cabeça real e regras de Blender.
- **reel-zona-segura:** margens de Reel e Story.
- **reel-pontilhado-cinetico:** quando o fundo de cima for o pontilhado.

## Variações de fundo (perguntar ou escolher pelo tema)
1. **Preto descendo para branco (padrão do Fies):** topo preto com linhas de caderno que somem no degradê, e a parte de baixo branca, onde fica o 3D.
2. **Branco descendo para preto:** o contrário. Bom para tema pesado no fim.
3. **Tudo branco:** caderno claro em cima e 3D sobre branco.
4. **Textura:** linhas de caderno OU pontilhado (o do reel-pontilhado-cinetico). A Priih gosta muito dos dois.

O degradê tem que ser longo e suave (uns 30% da altura), nunca uma faixa dura. O 3D não pode ser cortado pelo degradê: diminuir ou subir a cena antes de cortar.

## Layout que funcionou (palco 1080x1920)
- **Cabeçalho do lado a lado:** cabeças reais (só cabeça, contorno branco grosso, viradas para dentro, espelhar a foto se precisar), chip com nome, partido e ideologia (azul direita, vermelho esquerda) e linha divisória no meio. As cabeças têm tamanho visual parecido; formato de cabeça diferente engana, então conferir lado a lado.
- **Uma comparação por vez:** rótulo em cima e valor grande à esquerda e à direita, com auto-ajuste de largura (máx. ~340 px por lado, 10% de margem), sublinha pequena explicando. Nunca empilhar várias linhas ao mesmo tempo (fica aglomerado).
- **Nome do programa no título da linha** ("Sisu: pra entrar numa federal"), nunca só a explicação.
- **Letra miúda por cena:** com top próprio, nunca em cima de outro bloco nem perto da legenda; encurtar o texto se não couber em 2 linhas.
- **Selo de veredito:** pílula (ex. "✓ Verdade" verde), não carimbo torto.
- **Linha do tempo no fim** ("E hoje?"): ano grande, chip da pessoa e frase de 2 linhas sem palavra sozinha na linha.
- **Cards de estudo** (quando existir estudo, sempre mostrar): "Estudo do Tesouro, 2022" em cor tema, frase grande e explicação curta.
- **Fontes na base** e ideologia dos partidos na linha de fontes (Bolognesi et al. 2025).
- **Banner de 1 min** no canto superior direito, com o conteúdo de cima descendo ~78 px enquanto ele aparece.

## A história 3D embaixo
- Câmera com setViewOffset para a cena ficar só na metade de baixo; chão com alphaMap radial pra sumir no fundo.
- Bonecos com braços, mãos e mochila. Objetos que contam a regra: moedas (juro), cofre "FUNDO" (fundo garantidor), fiador fantasma (verde, bem visível, com "?" vermelho), cubinhos de calendário (meses, cores diferentes por lado), multidão entrando pelo portão (o momento preferido dela), prédios novos subindo, casa, prato e ônibus.
- Quando a narração fala de um grupo ("baixa renda"), mostrar a ação: o portão abre, um entra e outro chega no lugar.
- Tudo é função pura do tempo t (seek e render quadro a quadro).

## Narração (lição do Fies)
- **Gerar a narração inteira de uma vez** (ou em 2 blocos grandes) e cortar depois pelo silêncio, nunca uma gravação por cena. Cena por cena deixa cada trecho com entonação de primeira e última frase, e soa robótico.
- Palavras que a voz erra: escrever pra ela pronunciar (ex. "Fiés" pra não sair "fiz", "Pró-Uni"), mantendo a legenda certa.
- Velocidade que ela pediu no Fies: 1,10 na abertura, 1,05 até 1 min, 1,10 depois.
- Quebra de página da legenda: penalizar quebra depois de artigo, preposição, "juro", "real", "governo" etc. Conferir página por página.

## Render do MP4 (planejar o tempo antes)
- Aqui o 3D roda em CPU (swiftshader). Medido no Fies: ~2 s por quadro em cena leve e 6 s ou mais com multidão. Um vídeo de 3 min em 24 qps leva de 2 a 4 h.
- Acelerações sem perder qualidade visível:
  - parâmetro ?rs=0.7 (pixelRatio do 3D);
  - captura via CDP Page.captureScreenshot com optimizeForSpeed;
  - 24 qps;
  - um processo só (dois brigam pela CPU).
- Avisar a previsão de horário ANTES de começar. Nunca baixar qps nem qualidade sem perguntar a ela.
- Se precisar refazer um trecho, os quadros são determinísticos: refazer só aquele intervalo emenda perfeito.

## Pós-produção sem renderizar de novo
Tudo em cima do MP4 pronto, com ffmpeg e numpy:
- **Efeitos** (ElevenLabs sound effects, 1 geração cada, com duration_seconds definido, senão vem curto):
  - portão abrindo;
  - burburinho de multidão em loop, com volume seguindo quantas pessoas aparecem;
  - "pop" quando objetos aparecem;
  - subida nos prédios;
  - whoosh só nas 3 ou 4 trocas de cena principais;
  - sininho no fim.
  Ela achou "busy" quando tinha whoosh em toda troca.
- **Música de fundo:** loop calmo de 30 s (loop=true), com passa-baixa ~3,2 kHz pra tirar os agudinhos e volume BEM baixo (no Fies: RMS ~-44 dBFS antes da normalização), com ducking quando a voz fala. Ela pediu pra baixar várias vezes: começar baixo.
- **Pausas:** cortar até 0,35 s do meio dos silêncios maiores que 0,5 s, cortando vídeo e áudio juntos no mesmo quadro.
- **Volume final:** loudnorm I=-14, TP=-2 + limitador; conferir pico abaixo de 0 dBTP.

## Postar (ela quer que eu faça tudo)
- Hospedar o MP4 e a capa como manda o postar-agendar: cópia na pasta "Metricool public" do Drive (ID 1_i1tkJDOz0LNKsWOvcNnAmSmDhll2SQ3), sem perguntar, e cópia pra lixeira depois. Branch temporário do GitHub só como reserva enquanto o repo for público.
- Metricool brand 7092974: Instagram REEL + TikTok + Facebook REEL, com videoThumbnailUrl, legenda, 1º comentário e collaborators.
- Apagar a cópia pública (ou o branch, se usou) assim que o Metricool copiar.
- Collab só com @ confirmado (um @ errado pode travar o post). Os extras entram como marcação. A lista fica na aba "🤝 Collabs e marcações" da planilha News — Content Control.
- Depois:
  - salvar o MP4 e a capa na pasta do reel no Drive;
  - marcar a linha do tracker como postada, com os links;
  - deixar NOTE no ROTEIRO, incluindo o que acrescentar se for repostar.