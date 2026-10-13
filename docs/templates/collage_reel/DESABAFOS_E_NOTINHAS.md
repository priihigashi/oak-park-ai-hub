# Estilo "Desabafos e Notinhas"

Formato de Reel para @tentandochegaratevoce: um texto em 1ª pessoa (desabafo, nota, opinião) lido num **cartão de vidro líquido** sobre um **fundo vivo de ilustrações brasileiras** flutuando. Depois o cartão vai pro canto e entram notinhas curtas (o que dizem → o que é) até um fecho. Loop perfeito: o último quadro volta ao primeiro.

Primeira peça: `desabafo_v2.html` → "Contraponto" (out/2026, 59 s, sem som; trilha entra depois).
Versão descartada (não usar): `desabafo_a.html` (cartão de papel + emoji).

## Linha do tempo (59 s)
| tempo | o que acontece |
|---|---|
| 0–1,2 s | só o fundo e os stickers (= último quadro, fecha o loop) |
| 1,2–4,4 s | cartão de vidro nasce **atrás** dos stickers da frente e vem pra frente; aos 3,6 s troca de camada e fica por cima de tudo |
| 4,2–11 s | parágrafos entram um a um (sobe + desfoque → nítido), 0,8 s entre eles |
| até 29,5 s | leitura (texto parado, fundo vivo) |
| 29,5–31 s | cartão encolhe pro canto superior esquerdo (escala 0,4) |
| 31,5–47 s | 5 pares: pílula vermelha "DIZEM: …" + cartão com a resposta (título + 1 frase + fonte), um par a cada 3,5 s |
| 50,3–51,5 s | tudo desfoca e some; véu de vidro na tela inteira |
| 51,4–56 s | fecho em 3 linhas (branco / ouro / itálico) |
| 56,4–59 s | fecho e véu se dissolvem → volta ao quadro 1 |

## Visual
- **Fundo**: gradiente radial verde-bandeira `rgb(0,140,69)` que respira até azul royal `rgb(20,60,170)` no meio e volta (período = duração, então fecha o loop). Luz quente suave em `soft-light` passeando. Grão por cima, vinheta leve.
- **Para trocar a cor** (ex.: amarelo): mudar `g1`/`g2` na função `render` (linha `const g1=[0,140,69],g2=[20,60,170]`).
- **Cartão de vidro líquido**: `backdrop-filter: blur(22px) saturate(1.7)`, fundo branco 8–26%, borda 1,5 px branca 50%, brilho interno em cima, cantos 46 px, sombra verde-escura longa. Reflexo que varre o cartão quando ele entra (`--sh`).
- **Pílula "DIZEM:"**: vidro coral/vermelho, Fraunces itálico 780, etiqueta "DIZEM:" em Inter 700.
- **Tipografia**: Fraunces variável completa (eixo `SOFT 100` = serifa macia, igual à letra da referência Brasileirada), pesos 480–850; Inter variável para etiquetas e fontes. Arquivos em `assets/` (vêm de `@fontsource-variable/fraunces` e `@fontsource-variable/inter`).
- **Hierarquia do texto principal**: frase de abertura e frases-soco em `.h` (46 px, 760); corpo 32 px 520; a frase mais forte em `.rei` (60 px, 850) com a palavra final em ouro `#F2C94C`; números em ouro.

## Stickers (fundo)
- Ilustrações geradas por IA (Replicate, `black-forest-labs/flux-1.1-pro`, via `replicate_batch.yml` disparado pelo Composio). Prompt-base:
  > [assunto], Premium editorial illustration, Brazilian folk art meets contemporary gouache, visible brush and linocut texture, saturated palette deep green, royal blue, warm gold, coral pink, dignified, single subject centered with margin, isolated on plain flat pure white background, no text, no logos
- Recorte: fundo branco removido por flood-fill a partir das bordas, borda de papel 14 px (die-cut), sombra suave assada no PNG; versão `_b` desfocada para a camada de trás. Os PNGs prontos ficam no Drive (News › Reels_Shorts › v1_desabafo-contraponto › resources/stickers), porque `assets/` não vai pro repo: copiar para `assets/v2/` e gerar a versão `_b` com desfoque de 3 px (PIL `GaussianBlur(3)`).
- 3 camadas de profundidade (trás desfocada/menor, meio, frente maior). Camadas do meio e da frente andam na **mesma velocidade** (não se ultrapassam = não amontoam); 3 colunas fixas; fases igualmente espaçadas.
- Nossa Senhora Aparecida sempre na frente e 45% maior.
- **Diversidade obrigatória** (o público tem que se ver): Aparecida, baiana de branco, mãos com fitinha do Bonfim, evangélica, igreja; casal de homens, casal de mulheres, bandeira arco-íris, crianças no futebol (meia arco-íris); vaqueiro nordestino, gaúcho com chimarrão, indígena, nissei, motoboy, operário, agricultora, feirante; farmácia, entrega de chaves (moradia popular), merenda, enfermeira (SUS), formanda; arara, onça, caju, folhagem, bandeira do Brasil. Pessoas sempre com dignidade. Nunca duas pessoas do mesmo perfil lado a lado.
- Programas (Farmácia Popular, MCMV, Bolsa Família) aparecem pela cena, sem logo oficial.

## Regras de texto
- O desabafo é da autora: corrigir português e clareza, **nunca suavizar**. Pode deixar mais forte.
- Cada notinha: "DIZEM: frase da direita" → título que responde + 1 frase que explica pra quem não tem contexto + fonte pequena.
- As notinhas **apoiam o ponto da página**. Nunca usar uma notinha que acabe desmentindo a esquerda (ex.: "nórdico não é socialismo" saiu por isso).
- Número só com fonte.

## Produção
1. `./setup.sh` + `npm i @fontsource-variable/fraunces @fontsource-variable/inter` e copiar `fraunces-latin-full-*.woff2` e `inter-latin-wght-normal.woff2` para `assets/`.
2. Baixar os stickers do Drive para `assets/v2/` (ou gerar novos).
3. Editar texto/notinhas em `desabafo_v2.html`; `window.IMGS` = lista de stickers.
4. `PAGE=desabafo_v2.html node snap.js snaps 0 10 30 47 53` → conferir.
5. `node capture.js saida.mp4 desabafo_v2.html` (~25 min, o vidro é pesado) → `ffmpeg -crf 27` para mandar no chat.
