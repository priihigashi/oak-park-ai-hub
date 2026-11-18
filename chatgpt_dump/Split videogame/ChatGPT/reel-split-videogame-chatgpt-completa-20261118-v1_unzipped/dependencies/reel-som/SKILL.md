---
name: "reel-som"
description: "Som de todo reel: voz contínua sem fim de frase robótico, música/ambiente de fundo baixinho e efeitos especiais nas animações. Use em todo reel (todos os formatos, OPC incluso), quando ela disser que faltou som, ou que a voz ficou picotada/robótica."
---

# Som do reel: fundo + efeitos especiais

Por que existe: no reel dos indígenas (7/nov/2026) o vídeo ficou só com a voz. A Priih sentiu falta de som de trator quando a máquina aparece, de gente na aldeia, de um baque quando o NÃO cai, e de um fundo baixinho. Ela não quer pedir isso toda vez: todo reel já sai com som. Este skill também é o que ela chama quando diz "você esqueceu o som".

## Quando
- Em todo reel, de qualquer formato (colagem, pontilhado, timeline, split, 3D, desabafos, placar, quem-tem-culpa, OPC). Entra depois que a voz e os tempos estão prontos e antes de mostrar a prévia.
- Na voz grátis do rascunho também, pra ela já ouvir o vídeo completo.

## 0. Voz sem cara de "última frase" (vale pra voz grátis e pra ElevenLabs)
Por que existe: no reel do PLP 299 (13/nov/2026) a voz original, gerada num take só, ficou boa. As falas novas, geradas cena por cena e emendadas, ficaram picotadas, cada frase terminando como se fosse a última do vídeo. Medido: no take único a pausa mediana entre frases era cerca de 0,2 s e nenhuma passava de 0,5 s. Nas falas soltas a mediana foi de 0,4 a 0,5 s, com 6 a 14 pausas acima de 0,5 s por fala.

Regras:
- Gerar o roteiro inteiro num take só e depois cortar por cena. Nunca uma geração por cena.
- Se for trocar só um pedaço de um vídeo pronto:
  - Gerar com contexto. Na API do ElevenLabs, mandar previous_text com a frase original que vem antes e next_text com a que vem depois.
  - Se a ferramenta não tiver esses campos, gerar junto a última frase anterior e a primeira seguinte, e cortar as duas fora depois.
  - Mesmo modelo, mesma voz e mesmos ajustes do original. Anotar no ROTEIRO o modelo e os ajustes de cada take.
- Escrever pra fala corrida: menos frases curtas com ponto final. Ligar as ideias com vírgula, "e", "mas", "então", "só que". Cada ponto final vira uma descida de tom e uma pausa longa.
- Depois de gerar, medir as pausas antes de montar:
  - Toda pausa entre frases acima de 0,35 s cai pra uns 0,22 s.
  - Pausa dentro da frase (vírgula) não mexe.
  - Nunca cortar pausa abaixo de 0,15 s.
  - Nunca "cortar metade de todas as pausas" às cegas: some fim de palavra baixinho e as palavras grudam.
- Corte só em silêncio de verdade, com uns 80 ms de folga antes e depois da fala, e fade de 40 ms. Não cortar o rabo da última sílaba.
- Conferir ouvindo as emendas, uma por uma, antes de mostrar.

## 1. Fundo (sempre, baixinho)
- Escolher pelo tema: natureza/ambiente pra temas de terra, floresta e clima; música calma e neutra pra política e economia; pra OPC, algo leve de obra ou acústico.
- Oferecer 2 opções + "sem fundo" num seletor da prévia. Ela escolhe.
- Volume: bem abaixo da voz, uns 22 a 26 dB a menos, com ducking (o fundo abaixa enquanto ela fala). Nunca pode atrapalhar uma palavra.
- Fade de 1 s no começo e no fim.
- Fonte, nesta ordem: gravação real com licença livre (Wikimedia Commons CC0/CC BY; Freesound; YouTube Audio Library; Pixabay), com crédito no 1º comentário quando a licença pedir. Anotar a licença no ROTEIRO.
- Não gerar com IA "música indígena" ou de outra cultura específica: vira imitação. Se ela quiser, procurar gravação real com permissão e dar crédito.
- O ElevenLabs (sfx) não serve pra fundo longo: sai com 1 a 2 s. Usar pra efeito curto.

## 2. Efeitos especiais (mapa animação → som)
Cada animação que tem peso na história ganha um som curto, no mesmo frame em que ela entra:
- Selo/carimbo (slam): baque de carimbo no papel.
- Cartão que entra (deal): folha de papel.
- Chip/item que aparece (pop): pop suave.
- Algo que cai (o NÃO, placa): baque quando bate no chão.
- Máquina, trator, escavadeira no 3D: motor e esteira, por baixo, 2 a 4 s.
- Árvore derrubada: estalo de madeira e queda.
- Aldeia, gente, multidão: ambiente de vozes ao longe, sem palavras entendíveis.
- Casa, porta, despejo: porta batendo.
- Cadeado, lei, Constituição: clique de cadeado.
- Martelo de juiz, Congresso decidindo: batida de martelo.
- Placar/número contando: ticks suaves.
- Barras de gráfico crescendo: subida suave (opcional).
- Banner "toque pra continuar": continua sem som.
- Sem "whoosh" de transição por padrão (já incomodou antes); só se ela pedir.

Regras:
- No máximo um efeito a cada uns 3 s; efeito nunca em cima de nome, número ou negativa da voz (puxar 0,2 s antes ou depois).
- Volume: efeito uns 12 a 16 dB abaixo do pico da voz; motor e ambiente ainda mais baixos.
- Efeito curto gerado no ElevenLabs: sfx, eleven_text_to_sound_v2, 1 geração por som (custa uns 17 créditos cada). Guardar cada som numa biblioteca no Drive (News > Templates > Sons; criar se não existir) e reaproveitar antes de gerar de novo.

## 3. Como montar
- Os tempos vêm das palavras da voz (os mesmos data-in das animações). Montar com ffmpeg: voz + efeitos (adelay) + fundo (volume, ducking com sidechaincompress), e loudnorm na mistura final (voz por volta de -16 LUFS).
- Na prévia: o áudio já com efeitos, e um seletor de fundo (sem fundo / opção 1 / opção 2) que troca o arquivo mantendo o tempo e o play.
- No MP4: a mistura escolhida, assada no vídeo.

## 4. Conferir
- Ouvir no alto-falante do celular (é onde a maioria assiste): nenhum efeito cobre palavra, fundo não briga com a voz, nada estoura.
- Se algum som incomodar, medir voz, fundo e efeitos separados antes de trocar outra coisa.
- No ROTEIRO: lista dos efeitos (tempo, som, fonte/licença) e qual fundo ela escolheu.