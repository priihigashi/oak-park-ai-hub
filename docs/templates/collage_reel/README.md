# FLOW — Reel "Colagem Jornalística" (estilo Intercept/Agroecologia, versão nossa)

Segunda opção de formato de Reel para @tentandochegaratevoce, ao lado da **Dinâmica** (vídeo original + legenda PT-BR palavra por palavra + carimbos FATO/FALSO, ex.: "Gasolina: a culpa é do Biden?").
Na **Colagem**, o vídeo é 100% gráfico: fundo de cor chapada com textura de papel, recortes de pessoas (sticker com borda branca), objetos recortados, números que contam, recorte de jornal, carimbos, gráficos que crescem.

Primeira peça: `reel.html` → "Com o Lula, a comida subiu mais?" (72 s, out/2026).

## Quando usar qual
| Situação | Formato |
|---|---|
| Existe um vídeo de alguém falando algo que precisa ser checado | **Dinâmica** |
| O tema é um número / comparação / dado (preço, salário, votação, orçamento) e não tem vídeo bom | **Colagem** |
| Queremos refazer um vídeo de outra página com dados melhores | **Colagem** |

## Estrutura de roteiro (60–75 s) — "acusa → checa → o título tava errado"
1. **0–3 s GANCHO**: o título acusa (recorte de jornal + rosto). Ex.: "COM O LULA, A COMIDA SUBIU MAIS." Nunca entregar o veredito na capa. Tem que fazer os dois lados clicarem.
2. **3–6 s "SERÁ? BORA OLHAR OS NÚMEROS"** + fontes oficiais na tela (credibilidade logo de cara).
3. **Admitir o que é verdade** (carimbo VERDADE). Ex.: "tá caro sim". É isso que dá credibilidade com quem discorda.
4. **Ponto pra crítica**: um dado contra o lado que vai "ganhar" no final (ex.: café +72%).
5. **"Comparado com o quê?"**: cara a cara, mesmo período, mesma métrica.
6. **Provas** em 3–4 blocos de 5–8 s: contador → gráfico → fonte. Trocar algo na tela a cada 1,5–3 s.
7. **Ângulo político** (o que a nossa página quer mostrar, ex.: o agro reclama mas recebeu recorde).
8. **VEREDITO ~85%**: volta o recorte do gancho + carimbo FALSO + "O TÍTULO DESTE VÍDEO TAVA ERRADO."
9. **Fechamento**: VERDADE/FALSO resumido + "antes de repassar, confere o período e a fonte" + pergunta pra comentar.

## Regras de credibilidade (não negociáveis)
- Fonte em TODO número (instituição + série + período), em fonte mono pequena.
- Comparar igual com igual: mesmo índice, mesmo tipo de período; dizer quantos meses cada lado tem.
- Barras começam no zero, com rótulo.
- Nunca usar dado organizado por partido (o vídeo original usou "Núcleo Agrário do PT") — sempre ir na fonte primária (IBGE/SIDRA, DIEESE, BCB, TSE, FAO).
- Nada de "VOTE X". A página é de checagem, não de campanha.
- Veredito sobre a afirmação, não sobre a pessoa. Se for meio verdade, carimbar ENGANOSO, não FALSO.
- Nome do presidente: ok no vídeo; evitar na legenda e nas hashtags (alcance).

## Paleta (tokens da página) + fontes
- Tinta `#0E0D0B` · Papel `#F2ECE0` · Ouro `#C9A84C` · Vermelho alerta `#C8352B` · Ardósia `#3B5470`
- Carimbo VERDADE `#2E8B57` · FALSO vermelho escuro. Verde/vermelho só para veredito.
- Governo anterior = ardósia; governo atual = ouro (não usar cor de partido).
- Anton (títulos/números) · Fraunces 900 (manchete do recorte) · Fraunces itálico (frases) · JetBrains Mono (fontes, etiquetas).

## Vocabulário de shots (classes do motor)
`slam` (bate com tremida) · `pop` · `drop` (cai com quique) · `up`/`left` · `fade` · `stamp` (carimbo) · `.cnt` (número que conta) · `.bar`/`.col` (gráfico cresce) · `data-bob` (sticker respirando, tremidinha stop-motion 12 fps) · `data-o` (sai da cena) · `data-shake` (tremor de câmera).

## Pipeline técnico (determinístico)
1. `npm i @fontsource/anton @fontsource/fraunces @fontsource/jetbrains-mono @twemoji/svg playwright` → copiar fontes/emojis para `assets/`.
2. Rostos: foto editorial real (pasta resources/) → `python3 cutout.py` (recorte por cor de fundo) ou remove-bg. Sem foto: cartão de iniciais (nunca caixa vazia).
3. Escrever as cenas em `reel.html` (cada `<section class="scene" data-s data-e>`).
4. Prévia: `node snap.js snaps 1.5 10 20 …` → conferir quadros.
5. Render: `node capture.js video_noaudio.mp4` (30 fps, 1080×1920, quadro a quadro, sem perda de frame).
6. Áudio: `python3 audio.py events.json audio.wav` (trilha + whoosh/carimbo/ticks sincronizados pelos eventos da timeline; tudo sintetizado, sem direitos autorais). Locução opcional por cima.
7. `ffmpeg -i video_noaudio.mp4 -i audio.wav -c:v copy -c:a aac -shortest final.mp4`
8. Story doc + legenda (começa com COMPARTILHA NOS STORIES) + capa.

## O que o vídeo de referência (@ana_agroecologia) fez bem e onde pecou
Bem: ritmo de 2–3 s por ideia, rosto recortado com borda, contador de %, unidade de pontos (35 alimentos), gráfico de barras que vira, cores fortes por bloco.
Pecou: (1) é peça de campanha ("Vote 13") — perde quem discorda; (2) dados organizados pelo Núcleo Agrário do PT; (3) não diz o período dos "10 itens que caíram" (com o IPCA de set/2026 arroz e tomate já não caem); (4) esconde 2024 (+8,2%) e o café; (5) gráfico de barras sem escala/valores; (6) atribui causa (PAA/Conab) sem prova; (7) cebola +180% (IBGE: +183%); (8) Mapa da Fome usa média 2022–2024 (inclui 2022).

## Uso rápido
```bash
./setup.sh                                   # fontes, emojis, texturas
python3 cutout.py foto.png 0,0,800,1000 assets/pessoa.png 60   # recorte por cor de fundo (box x0,y0,x1,y1; tolerância)
node snap.js snaps 1.5 10 20                 # prévias
node capture.js video_noaudio.mp4            # render 30 fps + events.json
python3 audio.py events.json audio.wav       # trilha + SFX sincronizados
ffmpeg -i video_noaudio.mp4 -i audio.wav -c:v libx264 -crf 22 -c:a aac -shortest final.mp4
```
`reel.html` traz o episódio 1 ("Com o Lula, a comida subiu mais?") como exemplo completo de todas as cenas.
