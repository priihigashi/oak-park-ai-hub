# Repertório de movimento — Colagem Jornalística

Cada vídeo de referência que a Priih manda vira uma entrada aqui: **o que ele faz em movimento** (não só o quadro parado), **qual preset do motor reproduz isso** e **quando usar**.
Imagens/quadros de referência ficam no Drive (repo é público — nada de print de outra página aqui):
Drive › Videos › `colagem-reel-template` › `repertorio/ref_NN_<pagina>/`.

Demo renderizado de cada entrada: `repertorio.html` → `node capture.js demo.mp4 repertorio.html` + `python3 audio.py events.json a.wav 30`.

---

## REGRA DE USO — inspiração, NÃO cópia (ler antes de montar qualquer reel)
O repertório é uma **caixa de ferramentas**, não um molde. Uma referência ensina *movimentos*; ela nunca define o reel inteiro.
1. **Mistura obrigatória:** todo reel combina presets de **pelo menos 2 fontes** (REF 00 clássico + REF 01 + futuras). Nenhuma referência sozinha passa de ~40% das cenas.
2. **O tema decide o visual, não a referência:** primeiro o roteiro e o dado; depois escolher os presets que servem àquela cena. Nunca começar por "vou fazer no estilo X".
3. **Nunca reproduzir a sequência, a paleta ou a capa de uma referência.** Ex.: REF 01 = fundo preto + duotone vermelho/azul + palavra por batida + karaokê amarelo → no nosso reel usar 1–2 dessas ideias, com a NOSSA paleta (ardósia × ouro, papel, tinta) e nossas fontes.
4. **Pelo menos 1 coisa nova por reel** (combinação inédita, cor de bloco diferente, preset usado de outro jeito).
5. **Teste anti-cópia antes do render:** pôr o contact sheet do nosso reel ao lado do contact sheet de cada referência. Se alguém diria "é igual ao vídeo X" → trocar paleta/ordem/presets até não dizer.
6. **Variar entre episódios:** registrar no STORY doc quais presets/paleta foram usados; o próximo reel não repete a mesma combinação principal.

---

## REF 00 — motor clássico (episódio 1, "Comida subiu mais?")
Demo: `repertorio_classico.html` (30 s) — cada cena com o nome do preset embaixo:
pop + data-bob (sticker) · slam + data-shake (recorte de jornal) · up escalonado · left · fade (fonte) · receipt + .cnt (contador com tique) ·
stamp VERDADE/FALSO · drop com quique · .cnt gigante + data-o (troca de item) · data-shake-end · chip · .bar (cresce do zero) · .col (ano a ano, negativo em vermelho) · tag.
Linguagem: fundo chapado com textura de papel, cores por bloco (vermelho/tinta/ouro/papel/ardósia), Anton + Fraunces + JetBrains Mono.

---

## REF 01 — @doantidoto ("Nenhum dos dois", 86 s, out/2026)

**Linguagem:** fundo quase preto chapado (#121212), fotos em **retícula de linhas** (gravura), duotone vermelho/azul pra "os dois lados", **uma palavra gigante por batida** em grotesca pesada com ponto final ("FALAM." "FATO." "ÚNICO."), legenda **karaokê** amarela em itálico embaixo, tudo narrado em 1ª pessoa. Corte a cada ~1,5–3 s, nada parado.

### Movimentos observados → preset
| # | O que acontece na tela | Preset (fx.js / fx.css) |
|---|---|---|
| 1 | Rostos aparecem do preto com dissolve; ficam "respirando" com zoom lento | `data-a="dissolve"` + `data-kb="1.06"` |
| 2 | Dois perfis sobrepostos, um vermelho, outro azul, em linhas | `linescreen.py --ink "#E3241B"` / `--ink "#2D33E8"` + `mix-blend-mode:screen` |
| 3 | "NENHUM" nasce de pontinhos espalhados que se juntam | `data-a="scatter"` |
| 4 | Texto com borda de tinta que "ferve" (stop-motion 8 fps) | `data-boil="1"` |
| 5 | Troca de palavra a palavra com fatias + separação RGB | `data-a="glitch"` + `data-o` (saída instantânea, `data-od=".01"`) |
| 6 | Silhueta branca (papagaio) entra por trás e o texto vira preto onde cruza | `.sil` + `.knock` |
| 7 | "VALORES." repetido enchendo a tela de cima a baixo, rolando | `.stack` (`data-word`, `data-rows`) |
| 8 | Foto amarelo/verde (bandeira) com balões de quadrinho estrelados + faixa de papel rasgado + tremida e linha de VHS | `linescreen.py --ink "#F4D21F" --bg "#123d1c"` + `.burst` + `.torn` + `data-jit` + `data-vhs` |
| 9 | Olho no escuro abre → dissolve pra colagem (livros + globo) | `data-a="iris"` → `data-out="dissolve"` |
| 10 | Print de manchete desce de cima sobre a foto; troca por outra manchete com dissolve (antes/depois) | `.webcard` + `data-a="down"` + `data-out="dissolve"` |
| 11 | Cartão vermelho cheio de dados (lista) entra seco | `data-a="flash"` + `.bebas` |
| 12 | Legenda: palavra aparece apagada e acende amarela no tempo da fala, em "páginas" de 1–2 linhas | `.kar` (`data-words="palavra:t ... / próxima página"`) |
| 13 | Fechamento: foto escurece, logo da página no centro | cena com `data-in="fade"` |

### Fontes
- Palavra gigante: grotesca black apertada → **Inter Tight 900** (`.grot`, tracking −0,045em, entrelinha .86).
- Legenda karaokê: sans **itálico 800** → **Inter 800 Italic** (`.kar`), amarelo `#F2D21B`, apagado = 45%.
- Balões / cartões de dados: condensada → **Bebas Neue** (`.bebas`).
- Nossa marca continua valendo para fontes/carimbos (Anton · Fraunces · JetBrains Mono). Para usar o look Antídoto na NOSSA página, trocar o amarelo da legenda por `--kar-lit:#C9A84C` (ouro).

### O que aproveitar / o que não copiar
- ✅ Ritmo "uma palavra por batida" funciona muito bem pra **veredito** (FATO. / FALSO. / ENGANOSO.) e pra virada do roteiro.
- ✅ Retícula de linhas resolve o problema de foto feia/baixa resolução e unifica fotos de fontes diferentes.
- ✅ Karaokê = obrigatório quando tiver voz (funciona no mudo).
- ⚠️ É peça de opinião ("eu não gosto de nenhum dos dois, mas…") — não é checagem. Pra nós: manter o roteiro acusa → checa → título errado; usar a estética, não o formato opinativo.
- ⚠️ Duotone vermelho/azul = cor de lado. Na nossa página **ardósia (anterior) × ouro (atual)**; vermelho/verde só em veredito.
- ⚠️ Prints de manchete deles são de sites alinhados a um lado (Brasil de Fato, Fórum). Nós refazemos o card com **fonte primária + data** (`.webcard`).

---

---

## REF 02 — @ana_agroecologia ("O preço da comida", 74 s) — o original que inspirou o episódio 1
**Linguagem:** fundos de cor chapada e BEM saturados que mudam por ato (laranja → azul → papel → preto → vermelho), objetos em FOTO REAL recortada (banana, arroz, óleo, cebola — não emoji), rosto recortado gigante ancorado embaixo, condensada pesada em caixa alta, números em sans itálica branca, legenda pequena branca com contorno.
**Movimentos que valem ouro:**
- **Rosto Testemunha + Prateleira:** o rosto do responsável fica ancorado embaixo (cortado na testa/olhos) a cena toda; cada item entra no meio com pop, o contador sobe ao lado, e depois o item ENCOLHE e voa pra uma "prateleira" no topo, acumulando (+98,5% · +56% · +140%…). Ótimo pra lista de itens do mesmo responsável.
- **Pontos que Escorrem:** painel de papel sobe; pontos nascem pequenos e "escorrem" em fila (cobra) até formar uma grade; cada linha ganha cor e rótulo de categoria (laticínios, hortifruti…); depois a grade inteira vira preta e bate "NENHUM / FICOU MAIS BARATO". Ótimo pra "acompanhamos N itens".
- **Caixas que Empilham:** blocos coloridos com sigla (PAA · PNAE · CONAB) caem um sobre o outro.
- **Mapa com Faixa Torta:** mapa do Brasil + faixa branca girada que bate com o texto.
- **Barras Horizontais Longas:** ranking de 35 itens, barras crescem em 2 cores sobrepostas (antes × depois).
**Não copiar:** fim de campanha ("vote 13"), dados organizados pelo partido, período escondido, gráfico sem escala (ver REF 00 / episódio 1, onde corrigimos).
Cenas recortadas: biblioteca-cenas (ref02_agroecologia).

---

## REF 03 — @projeto.contraponto ("Feitos da direita que a esquerda não te conta", 103 s)
**Linguagem:** "carrossel animado" — cartões editoriais tipográficos sobre fundo verde-escuro com grão fino ESTÁTICO; 2 cores + creme (verde #03301F, amarelo #FCC13D, creme #FCF8F0, sálvia #7EAB9B); sem sombra; grid rígido (margem 7%, eyebrow sempre a 14,5% da altura, linha FONTE sempre a 78,5%); câmera 100% parada.
**Fontes:** Montserrat 800/900 (títulos, números) · Montserrat 600 caixa alta com tracking .15em (eyebrow, rótulos, FONTE) · serifa itálica (Newsreader Italic) nas frases-conclusão.
**Fotos:** duotone verde gigante de fundo (~30%); recorte P&B em CÍRCULO com a cabeça saindo pelo topo; recorte P&B sangrando no canto.
**Movimentos novos:** Linha que Sobe da Régua (texto nasce dentro de máscara, linha a linha, 0,25 s, atraso 0,12–0,17 s) · Painel que Sobe (cena nova sobe por cima, expo-out) · Limpa e Reconstrói · Contador Escala com milhar (2.477%) · Queda com Curva (número desce + curva em S desenhada) · Moeda que Gira (rotateY) · Barra que Encolhe com o Número · Rótulo que Viaja no topo da coluna · Lista que Empilha e Compacta · Retrato que Estoura do Círculo · Linha do Tempo de Pontos · Zero que Bate.
**Melhor que o nosso:** grid fixo, linha FONTE curta em todo dado, estrutura de série ("FEITO Nº 1"), contraste sans pesada × serifa itálica.
**Não copiar:** peça de campanha ("vote contra"), verde-amarelo politizado, dados de um lado só, fotos sem crédito, ritmo lento demais pro nosso DNA, marca d'água/outro do IG.

---

## REF 04 — @projeto.contraponto ("O que seria o governo Flávio Milei", 95 s)
**Linguagem:** motion graphics contínuo — poucos cortes (12), mas algo entra a cada 0,5–1,5 s, sincronizado com a fala; fundo grafite com vinheta radial (#2C2A2F → #17151A); 3 cores (vermelho #EA4339, off-white #F2EEE8, grafite) + cor semântica de país (azul Argentina); flat, sem grão, sem sombra.
**Fontes:** Montserrat 900 (títulos-soco, números gigantes) · Montserrat 800 tracking aberto (kickers) · serifa editorial (Source Serif 4 / Newsreader) nas manchetes e citações · Montserrat 600 na legenda.
**Legenda:** barra preta de largura total a ~75% da altura, frase inteira visível, palavras faladas em branco e as próximas em cinza (karaokê invertido).
**Fotos:** recorte P&B em DISCO cinza com a cabeça vazando pelo topo.
**Movimentos novos:** Máquina de Escrever com Cursor ▮ (assinatura) · Varrida Lateral (whip com borrão) · Ondas de Som · Plateia que Brota + Balões "…" · Retrato que Rola pra Dentro (disco) · Citação com Marca-texto · **Números Chutados** (dígitos aleatórios + etiqueta torta — perfeito pra checagem) · Lupa sobre o Documento · Empurrão Vertical · Zoom-Soco · Pop com Anel · Recibo que Estica + Risco · Ping de Lugar no mapa · Contador + Curva sincronizados · Grade que Acende (recolor seco) · Foguete (itens disparam com rastro) · Pedaço que Cai (barra perde pedaço com gravidade) · Cédulas que Enchem e Voam · Teclas Ctrl+C/V · Máscara que Revela · Grade-resumo de Cartões · Corte para Vazio.
**Melhor que o nosso:** cada número vira um OBJETO que se comporta como o dado (conta estica, barra perde pedaço, cédulas voam); montagem sincronizada com a fala; sistema rígido de 2 fontes / 3 cores; cartão de fonte com formato fixo (VEÍCULO · fio · manchete serifada · data).
**Não copiar:** rosto fundido de dois políticos (caricatura, não dado); projeção de inflação de outro país direto em reais (dado fraco); opinião de terceiro como fato; vermelho dominante; marca d'água/outro do IG.

---

## REF 05 — @joaoerre (Argentina → Brasil, 134 s) — "nada demais", só o melhor
**Vale:** cor forte chapada + papel com fibra (amarelo-limão #EFF90C, azul-marinho em degradê #0A1E3F→#18376D, papel #F0EEEF, carvão #232122, vermelho #CB142A só em seta/X) · **pílula marca-texto "gosmenta"** (cada linha com fundo arredondado que se funde nas quebras; Bricolage Grotesque 800) · **rosto rasgado ao meio** (metade de A + metade de B, emenda serrilhada com borda branca) · **letreiro grafite pingando** (Rubik Wet Paint com contorno grosso) · números largos (Unbounded 800) · **linha diagonal "de lá → pra cá"** ligando dois cartões · fundo de moedas reais em close.
**Movimentos:** Painel Inclinado que Sobe (borda torta ~8°, 0,18 s) · Lista que Acende em Pílulas · X Vermelho que Cancela · Seta que Despenca (desenha durante a fala) · Contador por Dígito na Pílula · Balão Digitado.
**Não copiar:** campanha; contrafactual de inflação de outro país sem fonte/período (se usar a linha diagonal: fonte, período igual e rótulo SIMULAÇÃO); amarelo + azul como identidade fixa (lê como cor de partido — só como cor de um ato); cenas paradas 10–20 s.

---

## Variações de template que esse repertório abre
1. **"Palavra por batida"** (kinetic type puro, fundo preto) — 30–45 s, pra opinião curta / resposta rápida / veredito. Sem gráfico; tudo `.grot` + `glitch` + `.kar`.
2. **"Retícula"** — o Colagem atual, mas com todas as fotos em `linescreen.py` (B&W) e lados em ardósia × ouro. Mais sério, cara de jornal impresso.
3. **"Quadrinho"** — `.burst` + `.torn` + foto em duas cores, pra mostrar ataques/frases reais de redes (com crédito na tela).
4. **"Antes/Depois de manchete"** — `.webcard` descendo + dissolve entre duas manchetes do mesmo índice em períodos diferentes. Ótimo pro bloco "comparado com o quê?".
5. **Híbrido Dinâmica + karaokê** — vídeo original da pessoa falando, legenda `.kar` palavra por palavra, carimbos do motor por cima.

## Como adicionar a próxima referência (REF 02…)
1. Quadros 1 fps + tiras 6 fps por trecho + 24 fps nas transições (`ffmpeg … fps=6,tile=12xN`).
2. Medir energia de movimento por segundo (onde é corte seco vs. movimento contínuo).
3. Listar movimentos → mapear pra preset existente; o que não existir vira preset novo em `fx.js` (documentar no cabeçalho).
4. Cena nova em `repertorio.html` mostrando o preset + render do demo.
5. Quadros/tiras/demo no Drive `repertorio/ref_NN_<pagina>/` + bloco novo neste arquivo + NOTE datada no doc TEMPLATE.


## Lote 2026-10-12 (baixados pelo workflow ref_fetch → Drive › colagem-reel-template › _entrada_refs: vídeo, folha de quadros, transcrição, áudio)
- **tut_01–06** — tutoriais de efeitos estilo Vox (parallax, corte na curva, página virando, TV antiga, cursor/contador/ondas, fundo em camadas ★). Viraram o KIT VOX (fx2.js, MOVIMENTOS §3b).
- **ref_06–08** — telas divididas em 3 / cartões, comparar países × períodos (download falhou na 1ª vez; nova tentativa com repetição). Opção de layout, não regra.
- **ref_09–11** — mais estilos (a analisar).
- **ref_12** — mapas Vox: foco radial + desfoque + linhas que se desenham → movimento 52.
- **ref_13** — "How we spend our time": corrida de barras por ano, fundo quase branco, serifa, barras suaves, ano grande no canto, etiqueta de evento ("RADIO ARRIVES"), régua do tempo → base do congresso.html v2. Também: coletar o SOM (pasta de áudios).
- **ref_14** — gráfico + mouse que clica no período e abre explicação → movimento 50.
- **ref_15** — estilo Vox com colagem de pessoas reais (favorito). **ref_16** — inserir personagem (favorito). **ref_17** — contar história misturando P&B e cor.
- **Sons**: cada referência tem `<nome>_audio.mp3` na pasta — biblioteca de sons/trilhas pra inspiração (não reutilizar áudio de terceiros em post publicado sem licença).
