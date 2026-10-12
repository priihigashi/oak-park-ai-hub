# Biblioteca de inspiração — movimentos, looks, fontes e detalhes

> **Leia assim:** tudo aqui é INSPIRAÇÃO, não receita. Escolha um, misture dois, mude a direção, ou invente um melhor.
> Nenhum reel usa a lista inteira e nenhum reel deve parecer cópia de outro (nem de uma referência, nem do nosso último).
> O que NÃO muda é o **DNA** (seção 1). Todo o resto varia de reel pra reel.

---

## 1. DNA FIXO — o que faz parecer "nosso" em qualquer reel
Isso aparece em TODO reel, seja qual for o look:
- **Paleta-mãe:** Tinta #0E0D0B · Papel #F2ECE0 · Ouro #C9A84C · Ardósia #3B5470 · Vermelho alerta #C8352B · Verde VERDADE #2E8B57. Um look pode puxar mais pra uma cor, mas não sai dessa família. Ardósia = governo anterior, ouro = atual. Verde/vermelho só em veredito.
- **Textura:** grão de filme sempre ligado (#grain) + fibra de papel nas cenas claras. Nada "liso de PowerPoint".
- **Assinatura de fonte de dado:** toda informação tem a linha mono pequena (JetBrains Mono) "INSTITUIÇÃO · SÉRIE · PERÍODO". É a nossa marca de credibilidade.
- **Carimbo de veredito:** VERDADE / FALSO / ENGANOSO, sempre o mesmo carimbo de borda grossa (stamp). Ele é o nosso "logo em movimento".
- **Arco do roteiro:** acusa → checa → "o título deste vídeo tava errado".
- **Handle** @tentandochegaratevoce pequeno em mono, embaixo, sempre no mesmo lugar.
- **Ritmo:** algo muda a cada 1,5–3 s; nada parado mais de 4 s.

## 2. LOOKS — escolha UM por reel como base (e quebre ele em 1–2 cenas)
| Look | Cara | Ideal para | Fontes sugeridas |
|---|---|---|---|
| **Papel & Recorte** (REF 00) | fundo de cor chapada com fibra, stickers com borda branca, recibo, fita crepe | preço, economia doméstica, temas do dia a dia | Anton + Fraunces + Mono |
| **Gravura Noturna** (REF 01) | fundo quase preto, rostos em anéis concêntricos, objetos em retícula de pontos | política, "os dois lados", personagens | Inter Tight 900 + Inter itálico + Bebas |
| **Jornal Impresso** | tudo em P&B com retícula, colunas, fios, manchetes serifadas, ouro só nos números | história, "quem votou o quê", Congresso | Fraunces 900 + Mono |
| **Dossiê** | papel kraft/ardósia, clipes, post-its, fotos 3×4 grampeadas, sublinhado de caneta | investigação, ligações entre pessoas, linha do tempo | Anton + Mono + manuscrito (Caveat) |
| **Placar** | estética de painel/placar eletrônico, números gigantes, contagem regressiva | votações, ranking, "quem ganhou" | Bebas + Mono |

| **Editorial Cartão** (REF 03) | cartões tipográficos, 2 cores + creme, grão estático, grid fixo, texto que sobe da régua | listas de feitos, séries ("Nº 1, Nº 2"), explicadores | Montserrat 800 + Newsreader Italic + Mono |
| **Explicador em Movimento** (REF 04) | grafite com vinheta, flat, cada número vira objeto que se mexe, digitação com cursor | economia, "quanto custa pra você", projeções | Montserrat 900/800 + Source Serif 4 |
| **Cor por Ato** (REF 02) | fundos saturados que mudam por ato, objetos em foto real recortada, rosto testemunha embaixo | preço, itens, comparação por categoria | condensada pesada + sans itálica pros números |

> Ideias de looks novos são bem-vindas. Um look novo vira linha aqui quando for usado.

## 3. MOVIMENTOS — nome · como é · ideal para · ideias
Cada um diz o que acontece quadro a quadro. Os presets entre `colchetes` são o jeito mais rápido de fazer no motor, mas não são o único.

### Entradas de personagem
1. **Cortina de Rosto** — o rosto (recorte) entra de cima pra baixo cobrindo a tela inteira como uma cortina; o fundo anterior some por trás dele. `down` com o recorte gigante (largura > 1080) + `data-kb`.
   *Ideal:* apresentar a pessoa acusada no gancho. *Ideia:* a cortina para no meio e o carimbo bate.
2. **Perfil Duplo** — dois perfis se olhando/sobrepostos, cada um numa cor (ardósia × ouro), entram do escuro com dissolve e respiram com zoom lento. `dissolve` + `data-kb` + `mix-blend-mode:screen`.
   *Ideal:* comparação entre governos/pessoas. *Ideia:* no fim, um dos perfis "apaga" (dissolve out) quando o dado o desmente.
3. **Sticker que Pula** — rosto recortado com borda branca estoura do centro e fica "respirando" com tremidinha de stop-motion. `pop` + `data-bob`.
   *Ideal:* tom leve, temas do dia a dia. *Ideia:* dois stickers que se empurram (um entra, o outro sai pela lateral).
4. **Holofote / Íris** — tudo preto; abre um círculo revelando um olho, um rosto ou um documento. `iris`.
   *Ideal:* "olha o que ninguém viu", revelar a fonte. *Ideia:* a íris segue o número que importa num print.

### Texto e palavras
5. **Palavra por Batida** — uma palavra gigante por vez, troca no corte seco com 2–3 quadros de glitch, ponto final no fim ("FATO."). `.grot` + `glitch` + `data-o` + `data-od=".01"`.
   *Ideal:* virada do roteiro, veredito, frase de impacto. *Ideia:* a última palavra fica e vira carimbo.
6. **Nasce do Pó** — a palavra aparece de pontinhos espalhados que se juntam. `scatter`.
   *Ideal:* palavra-chave do gancho. *Ideia:* no fim do vídeo ela se desfaz de volta (`data-out="scatter"`).
7. **Muro de Palavra** — a mesma palavra repetida enche a tela linha a linha e rola. `.stack`.
   *Ideal:* ênfase, repetição de discurso ("PRIVATIZAR. PRIVATIZAR."). *Ideia:* uma das linhas em ouro com o dado real.
8. **Manchete que Bate** — recorte de jornal entra grande, tremido, e assenta torto com fita crepe. `slam` + `data-shake` + `.clip` + `.tape`.
   *Ideal:* gancho que acusa. *Ideia:* no veredito ela volta e o carimbo FALSO bate por cima.
9. **Recorte sobre Silhueta** — forma branca (objeto/animal/mapa) entra por trás e o texto vira preto onde cruza. `.sil` + `.knock`.
   *Ideal:* metáfora visual (papagaio = repetição, mapa = região). *Ideia:* mapa do Brasil branco + nome do estado em knock.
10. **Legenda Karaokê** — fala aparece apagada e acende palavra por palavra no tempo da voz. `.kar`.
    *Ideal:* todo reel com voz. *Ideia:* palavra-chave da fala acende em ouro em vez de amarelo.

### Números e provas
11. **Contador com Tique** — número sobe do zero com som de tique e para com tremida. `.cnt` + `data-shake-end`.
    *Ideal:* todo dado principal. *Ideia:* o contador passa do valor e volta (exagero → verdade).
12. **Recibo** — nota de mercado sobe com itens e valores contando um por um. `.receipt` + `up` + `.cnt`.
    *Ideal:* preço, cesta, gasto público. *Ideia:* o recibo é rasgado (torn) no veredito.
13. **Barras Cara a Cara** — duas barras do zero, uma ardósia e uma ouro, crescem em tempos diferentes; resumo "por ano" entra embaixo. `.bar` + `.cnt`.
    *Ideal:* "comparado com o quê?". *Ideia:* barras viram dois copos enchendo.
14. **Ano a Ano** — colunas sobem em sequência, negativas descem em vermelho. `.col`.
    *Ideal:* séries históricas. *Ideia:* uma etiqueta voa até a coluna que contradiz o vídeo original.
15. **Cartão de Dados** — bloco de cor sólida estoura em branco e assenta com lista curta (3–4 itens + fonte). `flash` + `.bebas`.
    *Ideal:* listas (universidades criadas, leis aprovadas). *Ideia:* cada item entra com um tique.
16. **Manchete Antes/Depois** — print refeito desce sobre a foto; troca por outro com dissolve (mesmo índice, outro período). `.webcard` + `down` + `data-out="dissolve"`.
    *Ideal:* mostrar que a manchete escondeu o período. *Ideia:* as datas das duas ficam sublinhadas em vermelho.

### Transições e textura
17. **Corte Seco com Fatias** — cena seguinte entra fatiada com separação RGB por 0,2 s. `data-in="glitch"`.
    *Ideal:* mudança de assunto brusca. *Usar com moderação* (no máximo 2–3 por reel).
18. **Dissolve pelo Preto** — a foto some no escuro e a próxima nasce dele. `data-in="fade"` / `dissolve`.
    *Ideal:* momentos sérios, troca de personagem.
19. **Papel que Desce** — a cena nova desce por cima como uma folha (padrão do motor). `wipe`.
    *Ideal:* look Papel & Recorte.
20. **Fita Antiga** — linha de tracking + flicker leve por cima. `data-vhs`.
    *Ideal:* arquivo, declaração antiga, "em 2018 ele disse…".
21. **Câmera na Mão** — tudo treme levemente o tempo todo. `data-jit`.
    *Ideal:* briga, ataque, tensão.
22. **Balão de Quadrinho** — frase real de rede social dentro de balão estrelado + crédito em papel rasgado. `.burst` + `.torn`.
    *Ideal:* mostrar ataques/frases reais (sempre com crédito).

### Novos do REF 02 / 03 / 04 (inspiração — combine, adapte, ou invente melhor)
23. **Rosto Testemunha + Prateleira** (REF 02) — rosto do responsável ancorado embaixo, cortado nos olhos, a cena toda; cada item entra no centro, conta, e encolhe pra uma prateleira no topo que vai acumulando. *Ideal:* "tudo que subiu na gestão X". *Ideia:* no fim a prateleira inteira cai em cima do rosto.
24. **Pontos que Escorrem** (REF 02) — pontos nascem em fila e escorrem até formar grade; linhas ganham cor/rótulo por categoria; depois tudo vira uma cor só e bate a conclusão. *Ideal:* "acompanhamos N itens". *Ideia:* os pontos que contradizem o vídeo original piscam em ouro.
25. **Linha que Sobe da Régua** (REF 03) — cada linha de texto nasce cortada dentro de uma máscara e sobe 30–40 px em 0,25 s, uma depois da outra. *Ideal:* todo texto de leitura; dá acabamento premium. *Ideia:* combinar com Painel que Sobe.
26. **Painel que Sobe** (REF 03) — a cena nova sobe por cima da antiga como uma folha sólida, rápido e com cauda suave. *Ideal:* virada de ato.
27. **Retrato que Estoura do Círculo / Disco** (REF 03/04) — recorte P&B dentro de um círculo de cor, com a cabeça saindo pelo topo; entra em pop ou deslizando. *Ideal:* apresentar quem falou/votou. *Ideia:* círculo ardósia (governo anterior) ou ouro (atual).
28. **Máquina de Escrever com Cursor** (REF 04) — rótulo digitado letra a letra com cursor de bloco ▮. *Ideal:* kicker, nome, "a voz que dita". *Ideia:* digitar a frase exata do político entre aspas.
29. **Números Chutados** (REF 04) — os dígitos trocam aleatoriamente a cada quadro e nunca assentam; uma etiqueta torta bate: "SEM FONTE". *Ideal:* desmentir número inventado. Perfeito pra checagem.
30. **Lupa sobre o Documento** (REF 04) — documento apagado; uma lente circular nítida passeia lendo. *Ideal:* "o que diz o texto da lei/plano".
31. **Citação com Marca-texto** (REF 04) — frase em serifa aparece e um marca-texto passa por trás da palavra-chave. *Ideal:* destacar a frase exata da fonte.
32. **Zoom-Soco** (REF 04) — a cena velha explode pra 4× em 2 quadros e a nova assenta de 1,12 → 1. *Ideal:* mudar de assunto.
33. **Objeto que Se Comporta Como o Dado** (REF 04) — recibo que estica com o total contando; barra que perde um pedaço que cai com gravidade; cédulas que enchem a tela e voam; itens que disparam como foguete. *Ideal:* todo número de impacto no bolso. *Regra:* o movimento tem que ser fiel ao dado (se caiu 39%, cai 39% da barra).
34. **Contador + Curva Sincronizados** (REF 03/04) — o número conta enquanto a curva se desenha; uma segunda curva (inflação) entra pra comparar. *Ideal:* "subiu X% contra Y% da inflação".
35. **Linha do Tempo de Pontos** (REF 03) — eixo se desenha e os anos acendem um a um. *Ideal:* quem começou o quê, quando.
36. **Legenda em Barra (karaokê invertido)** (REF 04) — frase inteira visível numa barra escura, palavras faladas acendem. *Variação do `.kar`.*

### Clipe real do personagem — ASSINATURA DA PÁGINA (sempre que existir)
37. **Da Boca Dele** — um trecho curto (2–6 s) de vídeo REAL da pessoa falando, recortada (cabeça ou corpo) sobre o nosso design, com legenda karaokê e crédito "FONTE · VEÍCULO/CANAL · DATA". Pode ser fala sobre o tema ou comportamento público que mostre quem a pessoa é. *Ideal:* todo reel sobre político — é o que diferencia a gente de quem só usa foto parada. *Regras:* o trecho mantém o sentido que tinha no vídeo inteiro (assistir antes e depois do corte); data e fonte na tela; guardar link original no STORY doc.

## 4. FONTES — combinações (uma por reel, no máximo 3 famílias)
- **Clássica da casa:** Anton (título) · Fraunces 900/itálico (manchete e frase) · JetBrains Mono (fonte do dado).
- **Grotesca premium:** Inter Tight 900 apertada (palavra gigante com ponto) · Inter 800 itálico (legenda) · Mono.
- **Condensada de cartaz:** Bebas Neue (listas, cartões) · Fraunces itálico (frases) · Mono.
- **Editorial (REF 03/04):** Montserrat 900/800 (títulos e números) · Montserrat 600 tracking .15em (rótulos) · Newsreader Italic ou Source Serif 4 (frases, manchetes).
- Ideias pra testar: Archivo Black, Space Grotesk, IBM Plex Serif, Caveat (anotação de caneta no Dossiê).
- Regra: só uma fonte "de impacto" por reel; o mono de fonte do dado é fixo.

## 5. DETALHES PREMIUM — checklist antes do render
- [ ] Assuntos GRANDES e cortados pela borda (rosto de 1100–1400 px), nunca pequeno no centro de um fundo vazio.
- [ ] Camadas: fundo → foto com textura → texto → detalhe (fita, carimbo, fonte). Pelo menos 3 camadas por cena.
- [ ] Toda foto tratada do mesmo jeito no reel (anéis, pontos, linhas ou recorte com borda), nunca foto crua misturada.
- [ ] Texto com borda "fotocopiada" (`data-rough`) ou fervendo (`data-boil`) nas palavras gigantes; nunca vetor liso.
- [ ] Sombras duras (box-shadow deslocado), nunca sombra borrada genérica.
- [ ] Nada parado: zoom lento (`data-kb`) ou deriva (`data-drift`) em toda foto.
- [ ] Respiro: margens de 60 px, nada colado nas zonas de UI do Instagram (topo 220 px, base 300 px).
- [ ] Som acompanha cada entrada (whoosh, tique, carimbo, zap).
- [ ] Grid fixo: rótulo/eyebrow e linha de FONTE sempre na mesma altura em todas as cenas (REF 03).
- [ ] Pelo menos 1 clipe real "Da Boca Dele" quando o tema for uma pessoa (§3, nº 37).
- [ ] Cada número de impacto vira objeto que se comporta como o dado (§3, nº 33).
- [ ] Teste anti-cópia: lado a lado com as referências e com o último reel.

## 6. Biblioteca de cenas (clipes de 1 cena)
No Drive: colagem-reel-template › biblioteca-cenas › <categoria>/ — cada arquivo `categoria__referencia__cena.mp4` + miniatura .jpg. Índice: `CATALOGO_CENAS.csv` (categoria, referência, trecho, movimentos, ideal para). Antes de montar uma cena, abra a categoria correspondente (ex.: grafico-barras, linha-do-tempo, apresentacao-personagem) e veja 2–3 opções de referências diferentes; escolha, misture ou invente.

## 7. Como essa biblioteca cresce
Cada vídeo de referência novo: extraímos os movimentos (quadro a quadro), os detalhes de design (textura, fontes, camadas, timing) e entramos aqui com nome próprio. Se um movimento já existe, só acrescentamos a variação. Fonte de cada movimento fica no REPERTORIO.md.
