---
name: "reel-motion-limpo"
description: "Reels 2D em estilo motion design limpo (fundo claro, formas chapadas, molas, texto subindo por máscara, inundação de cor), feitos só com código HTML + Playwright + ffmpeg. Use quando Priih pedir o estilo 'limpo' ou 'claude motion design'."
---

# Reel motion design "limpo" (2D, só código)

Estilo inspirado no repositório MIT howseen-ai/claude-motion-design (HTML + Playwright + ffmpeg, sem After Effects, sem licença do Remotion). NÃO é 3D. Para 3D, usar Three.js com outra abordagem.

## Visual
- Fundo claro quente (#f5f5f2) ou tinta (#0b0b0c); cor tema do dia (regra dos dias da semana da Priih) como acento. Preto, branco e vermelho como fundos companheiros.
- Formas chapadas (SVG) sem gradiente decorativo, sem glow, sem vidro fosco.
- Fonte moderna, limpa, bold, levemente arredondada (ex.: Geist 700/800 ou Rubik 800). Nunca serifa de template.
- Texto entra por máscara: cada palavra sobe de translateY(105%) dentro de overflow:hidden, com stagger de ~55 ms e leve rotação (3 a 4 graus) que zera. Palavra de destaque na cor tema.
- Troca de cena por "inundação": um círculo nasce de um objeto da cena e cobre o quadro inteiro em 0,3 a 0,35 s (raio até o canto mais distante x1,05), depois a próxima cena já entra em movimento.
- Molas (spring de forma fechada) para tudo que aparece; nada linear. Easings: cubic in-out, out.
- Câmera = um transform num container: deriva sutil sempre viva (nenhum quadro congelado, exceto o final) e um "punch" de +0,03 com decaimento exponencial nas palavras-chave.
- Elementos compartilhados entre cenas (o objeto da cena anterior carrega a transição).
- Elementos entram na palavra falada e saem quando o texto seguinte chega.

## Motor (um arquivo HTML)
- Tudo calculado a partir do tempo dentro de `window.seek = async (t) => {...}`. Sem transições CSS, sem timers, sem estado entre quadros. Declarar constantes antes do primeiro seek. `window.ready = true` depois de fontes e imagens carregarem.
- Palco lógico 1080x1920 escalado por transform. z-index em toda camada.
- O preview toca chamando o MESMO seek(t) num loop de requestAnimationFrame (único lugar com relógio). O render nunca usa esse loop.

## Regras de reel da Priih (sempre)
- ZONA SEGURA Reels + Stories (skill reel-zona-segura): TEXTO só em x 150-915 e y 268-1680; imagem e fundo podem ir até a borda. @ em y 1626 e fonte em y 1668. Legenda falada entre x 190 e 915. Antes do MP4, conferir com a moldura simulada do Story e do Reel e mostrar a ela.
- Legenda falada: sempre duas linhas cheias por página, cor seguindo a voz palavra por palavra (palavra atual na cor tema); legenda baixa, inteira na tela; nada de nota miúda perto ou abaixo da legenda.
- Linha de fonte sempre no mesmo lugar, bem embaixo, abaixo do @handle.
- Títulos preenchem as linhas por igual (nunca uma ou duas palavras sozinhas numa linha).
- Texto pequeno legível em celular pequeno (nota 23px, notas 24px, fonte 22px, sublabels 20px no palco 1080). Dúvidas e pontos importantes não viram nota miúda: viram cena ou bloco de perguntas e respostas no fim.
- Frase que abre bloco começa com maiúscula. Sem travessão. Números com ponto de milhar.
- Conferir quebras de linha tela por tela antes de entregar.
- Primeiros 10 s já ensinam algo do tema; o mais importante dentro do primeiro minuto; banner "toque pra continuar assistindo" + "vendo pelo story? toque aqui" de 0:50 a 1:00 em espaço livre, pulsando leve.
- Narração de rascunho com voz grátis da Microsoft (edge-tts, pt-BR, com WordBoundary para sincronizar legenda); ElevenLabs só no final aprovado, 1 take. Na nuvem, o edge-tts roda no workbench do Composio (a rede local bloqueia o servidor da Microsoft).

## Fluxo
1. Roteiro em frases corridas, tom de conversa (não robótico), mostrando expertise e explicando em seguida.
2. Pasta e documentos no Drive + prompt pronto de auditoria pro ChatGPT: seguir o skill reel-pasta-roteiro-auditoria (pasta v<N>_<slug> na pasta de reels do nicho, docs ROTEIRO e TRANSCRIÇÕES, resposta com o texto pronto pra colar com os links).
3. Narração rascunho com tempos por palavra.
4. Mapa de cenas ancorado nas palavras (cada visual entra na palavra).
5. 4 stills de teste (Playwright: seek(t), esperar 2 requestAnimationFrame, screenshot) -> olhar -> corrigir.
6. Preview como artifact (tamanho celular): play/seek, pular 5/10/30 s, velocidades 1/1,05/1,1/1,2/1,5/2/3x, caixa de notas logo abaixo das velocidades com botão copiar, campos prontos de legenda do post e primeiro comentário, botão de download (vídeo quando existir), aba com o vídeo original se for baseado no vídeo de outra pessoa. Republicar no mesmo link a cada rodada dizendo o que mudou.
7. MP4 só depois da aprovação: Playwright quadro a quadro (seek(t) + 2 rAF + screenshot), 30 fps, ffmpeg H.264 -preset veryfast, yuv420p, +faststart; conferir contagem de quadros e procurar "pulos" (diferença entre quadros muito acima dos vizinhos). O MP4 final vai pra mesma pasta do conteúdo no Drive.

## Limites
- Não rodar scripts que baixam coisas de sites externos sem necessidade; a rede da nuvem é restrita.
- Gastar pouco: testar trechos curtos primeiro, sem agentes paralelos a menos que a Priih peça.