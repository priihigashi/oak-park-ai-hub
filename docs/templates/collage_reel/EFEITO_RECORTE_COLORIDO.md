# Efeito "Recorte colorido + fundo P&B + TV antiga"

Status: EM TESTE (1º uso no reel v1_flavio-coautor, prévia v2 de 18/10/2026). Se a Priih aprovar, vira opção fixa no skill reel-colagem-jornalistica.

## O que é
- A pessoa que fala fica COLORIDA; o resto do quadro fica PRETO E BRANCO, escurecido e com contraste.
- Halo branco sutil em volta da pessoa (efeito sticker leve).
- Por cima do vídeo (e por baixo do texto): textura de TV antiga = linhas de varredura + vinheta arredondada + cintilação leve.
- Vídeo sempre SEM SOM, só como fundo que se mexe.

## Quando usar
- Clipes curtos do político falando (entrevista, coletiva, vídeo do próprio canal).
- Foto parada também funciona (mesmo efeito, com zoom lento).
- Funciona melhor com 1 pessoa grande no quadro. Em coletiva, os microfones e repórteres também ficam coloridos (fica bonito).

## Como fazer (passo a passo)
1. Script: colorpop.py (na pasta do Drive News › Templates › Videos › efeito-recorte-colorido-tv-antiga e aqui priihigashi/oak-park-ai-hub, branch feat/collage-reel-format, docs/templates/collage_reel/colorpop.py).
2. Modelo de recorte: MediaPipe selfie_segmenter.tflite (baixar de storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite; apontar com SEG_MODEL). ~30 ms por quadro, 1 min por clipe de 7 s.
3. Comando: python3 colorpop.py entrada.mp4 saida.mp4 cx fps início duração zoom cy
   - cx/cy = onde está o rosto no quadro original (0 a 1). Ex.: 0.57 24 0 7 1.35 0.40
   - zoom maior corta legenda queimada no rodapé do vídeo original.
4. No reel: video muted como fundo + div .crt + div .shade (ver CSS abaixo). Legenda e textos por cima.
5. NÃO use o modelo selfie_multiclass (1 s por quadro, lento demais).

## CSS da TV antiga
.crt: repeating-linear-gradient(180deg, rgba(0,0,0,.22) 0 2px, transparent 2px 5px) + radial-gradient vinheta (transparent 58% -> rgba(0,0,0,.85) 100%), mix-blend-mode multiply; opacidade oscila 0.85-1 (cintilação) e as linhas descem 60 px/s.

## Direitos de imagem (checado 18/10/2026)
- Agência Senado (fotos): livre, citando Agência Senado e autor. OK.
- TV Senado (vídeo): PROIBIDO cortar, editar ou usar em conteúdo político. Não usar, nem quando outro canal reposta (ex.: canal do Esperidião Amin usa imagem da TV Senado).
- Canal Gov / TV BrasilGov no Wikimedia Commons: CC BY 3.0, pode com crédito.
- Vídeo do próprio canal do político e trechos curtos de TV/jornal: direito de citação (trecho curto, crédito na linha de fonte, sem som).

## Exemplos (pasta exemplos/)
- exemplo_estudio.mp4 (vídeo do canal de Flávio Bolsonaro)
- exemplo_coletiva.mp4 (coletiva, reprodução Metrópoles)
- exemplo_foto_amin.jpg (foto Agência Senado, CC BY 2.0)
- folha_quadros.jpg (6 clipes lado a lado)
- Prévia ao vivo com o efeito aplicado: https://claude.ai/artifact/KmSVEhhdsg1r6KMwkVdYQJ

## Referência de estilo "Nikolas – Plano de Governo"
Checado em 18/10/2026: esse estilo NUNCA foi salvo como skill ou referência. Só existe o estilo de carrossel "NIKOLAS DISSE" dentro do skill transcribe-comment-create. Pendente: criar a pasta nikolas-plano-reel-template aqui em Templates › Videos quando a Priih mandar de novo o vídeo de referência.
