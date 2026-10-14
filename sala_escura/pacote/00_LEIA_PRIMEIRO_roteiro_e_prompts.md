# SALA ESCURA — roteiro, cenas e prompts

**Reel vertical 9:16 (1080×1920), ~1:37. Versões PT e EN.**
Ideia: uma mulher numa sala escura liga a TV. Primeiro passa o Trump rindo com o Zuckerberg, depois ela troca de canal e entra o vídeo do Tio Sam ("Eu não preciso invadir o seu país. Eu só preciso invadir a sua opinião."). No final ela diz "Ah, até parece", troca de volta para o Trump e diz "Ah, eu adoro o Trump."

## Regra mais importante

**O que passa na TV tem que ser o vídeo real.** Nenhuma IA pode gerar o Trump, o Zuckerberg ou o Tio Sam. Nas cenas geradas, a tela da TV deve ficar **lisa e clara (branco-azulada), sem nada**. Depois eu encaixo os vídeos reais na tela e acerto a perspectiva.

Regras para todas as cenas geradas:
- câmera parada (tripé), sem zoom e sem movimento de câmera;
- sala escura, à noite, com um abajur quente no canto esquerdo;
- a mulher nunca mostra o rosto (sempre de costas ou por cima do ombro);
- realista, como filmagem de verdade, sem cara de IA;
- sem texto e sem logo.

---

## Cena 1 — Sala vazia (1 s)
- **Imagem:** `cena01_sala_vazia.png`
- **Movimento:** nenhum, é um plano parado. Só a luz do abajur.
- **Prompt (opcional, se quiser animar):** "Use this exact image as the first frame. Static locked-off tripod shot. Dark Brazilian apartment living room at night, only a warm lamp in the left corner. Nothing moves except a very subtle flicker of the lamp light. Photorealistic, real footage, film grain. 3 seconds."

## Cena 2 — Ela entra e para na frente do assento da direita (2–5 s)
- **Imagem inicial:** `cena01_sala_vazia.png`
- **Imagem final:** `cena02_ela_no_assento.png`
- **Referência do que já existe:** `ref_cena02_entrada_seedance.mp4`. Ela atravessava o sofá como um fantasma, então eu cortei esse trecho.
- **Prompt:**
"Start frame = first image, end frame = second image. Static locked-off tripod camera behind the sofa, no camera movement. A woman with shoulder-length dark wavy hair, loose grey t-shirt and dark shorts walks into the dark living room from the RIGHT side of the frame, walking in the space BETWEEN the sofa and the TV wall (she never passes through the sofa), and stops standing in front of the right seat of the sofa, facing the TV, her back to the camera. Natural, realistic walking, real human weight and timing. TV stays off. Photorealistic, real footage, no morphing. 5 seconds."

## Cena 3 — Close por cima do ombro, mão no controle (2 s)
- **Imagem:** `cena03_close_controle.png`
- **Prompt:**
"Use this image as the first frame. Static camera, shallow depth of field. She is seated on the sofa; her hand holding the TV remote is in focus. Her thumb presses the power button once; tiny natural hand movement. The room and the TV in the background stay blurred and the TV stays OFF (no light change). Photorealistic, real footage. 3 seconds."

## Cena 4 — Por trás do ombro: TV liga com Trump e Zuckerberg (3,5 s)
- **Imagem:** `cena04_06_por_tras_do_ombro.png`
- **Na TV (eu encaixo):** `TV_trump_zuckerberg.mp4`, o Zuckerberg falando no ouvido do Trump e os dois rindo (clipe da @samiragharaee).
- **Prompt:**
"Use this image as the first frame. Static locked-off camera behind her shoulder. She sits on the sofa holding the remote and slowly lowers her arm, small natural movements of her head and hair. The TV screen stays a plain, flat, bright white-blue rectangle with NOTHING on it (it will be replaced in editing). Photorealistic, real footage. 5 seconds."

## Cena 5 — Troca de canal: chiado (0,4 s)
Eu faço na edição, sem IA.

## Cena 6 — Mesmo tipo de ângulo, agora com o Tio Sam (3 s)
- **Imagem:** `cena06_por_tras_sentada.png`
- **Na TV (eu encaixo):** `TV_tio_sam.mp4` (vídeo do @rodrigogonzalezgeo, já sem título, sem legenda antiga e sem o nome de usuário).
- **Prompt:**
"Use this image as the first frame. Static locked-off camera from behind the sofa. She sits still watching TV, tiny natural breathing and head movements only. TV screen stays a plain flat bright white-blue rectangle with nothing on it. Photorealistic, real footage. 5 seconds."

## Cena 7 — TV de perto, sem ela (≈79 s)
- **Imagem:** `cena07_tv_de_perto.png`
- **Movimento:** nenhum. Plano parado; só a TV passa o vídeo do Tio Sam até o fim. Não precisa de IA.

## Cena 8 — Final (7 s)
- Mesmo ângulo da cena 6. O vídeo do Tio Sam termina e a TV escurece.
- Ela: **"Ah, até parece."** (EN: "Yeah, right.")
- Chiado de troca de canal, depois o ângulo da cena 4 com o Trump e o Zuckerberg rindo.
- Ela: **"Ah, eu adoro o Trump."** (EN: "Oh, I love Trump.") Fade para preto.
- As falas dela estão como legenda. Se quiser voz, dá para gravar ou gerar depois.

---

## Arquivos nesta pasta
| Arquivo | O que é |
|---|---|
| `cena01_sala_vazia.png` … `cena07_tv_de_perto.png` | Imagens de cada cena (primeiro frame) |
| `TV_trump_zuckerberg.mp4` | Clipe real para a TV, horizontal, já cortado |
| `TV_tio_sam.mp4` | Vídeo real do Tio Sam para a TV, limpo |
| `ref_cena02_entrada_seedance.mp4` | Animação atual da entrada (só referência) |
| `REF_versao_atual_PT.mp4` / `REF_versao_atual_EN.mp4` | Montagem atual completa (referência de ordem e tempo) |
| `legendas_PT.ass` / `legendas_EN.ass` | Legendas com tempo exato |

## Como devolver
Gere as cenas 2, 3, 4 e 6 no ChatGPT, com a tela da TV lisa, e coloque os vídeos nesta pasta com o nome `GERADO_cena02.mp4` etc. Eu encaixo os vídeos reais na TV, coloco som e legendas e fecho as versões PT e EN.

**Créditos no post:** @rodrigogonzalezgeo (Tio Sam) e @samiragharaee (Trump e Zuckerberg).
