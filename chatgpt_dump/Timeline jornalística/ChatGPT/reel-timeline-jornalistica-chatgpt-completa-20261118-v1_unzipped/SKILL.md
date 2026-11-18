---
name: "reel-timeline-jornalistica"
description: "Use when making a TIMELINE Reel for @tentandochegaratevoce: story told by navigating a timeline panel (overview → zoom into each milestone → full panel at the end), voice + cards + optional short host/avatar clips."
---

## Durabilidade e versão ChatGPT · 18/11/2026
Esta é uma cópia versionada para ChatGPT/Codex; o original fica em `../original/`. Antes de concluir uma alteração, preservar nova versão no Drive Creations > Tools, Skills & Flows > Skills > Reels e Carrosséis > formato > ChatGPT (usar as pastas existentes criadas por Claude) E no GitHub privado `priihigashi/news`, em branch/PR sem merge. Conferir arquivo, pasta, tamanho/hash e links nos dois destinos; registrar pendência real se algum falhar. Nunca considerar apenas o arquivo local como entrega durável; GitHub não substitui Drive. Não sobrescrever versões existentes nem alterar a versão Claude. Consultar `MANIFESTO.json` e o índice desta entrega para origem e comprovantes.

As regras atuais de `regras-priih` prevalecem sobre conflitos históricos abaixo, inclusive aprovação antes de MP4 e voz paga. Os arquivos locais citados no texto histórico não são presumidos disponíveis no celular. Dependências preservadas separadamente em `compartilhadas/`, sem fundir os formatos.


# Reel — TIMELINE JORNALÍSTICA

> **Antes de roteirizar, e já no primeiro vídeo de referência:** seguir também o skill reel-pasta-roteiro-auditoria (pasta v<N>_<slug>, TRANSCRIÇÕES com cada vídeo numerado, linha no tracker, LISTA DE FEEDBACK DA PRIIH no topo do ROTEIRO, roteiro em tabela narração | animação de cada frase, conexões entre blocos, prompt de auditoria). Ele vale junto com este skill.


Formato irmão da Colagem (`reel-colagem-jornalistica`) e da Checagem ao Vivo. Mesmo motor, mesmas cores/fontes, mesma regra de pesquisa e de voz — o que muda é o ROTEIRO: a história anda pelo tempo, e a câmera navega um painel.
Use quando o tema é "como chegamos aqui" (sequência de fatos, governos, leis, votações, escândalo que se desenrola). Tema de um número só / comparação → Colagem. Tem vídeo de alguém falando → Checagem ao Vivo.

## 0. Antes de tudo
1. Ler inteiro (com NOTES) o doc TEMPLATE da Timeline 1KSHnI7xiKpTDciP8NlAy6H23n-ZU4o5wgPyhPHB77yM, na pasta Drive News › Videos › `timeline-reel-template` (1DGTLhCkSVx9UoOlzMuG_ep8cGzPXI-cQ). Referências em `repertorio/ref_NN_<pagina>/` (REF 01 = 15NwXNXxPKUMZPeEvu3hskPddQSIAPBDU: vídeo completo, quadros a cada 5 s, quadros-chave por cenário, folhas de contato, transcrição).
2. Perguntar (uma pergunta, com opções): **apresentador?** — (a) sem rosto, só voz + painel (padrão, mais barato) · (b) clipes curtos de avatar/rosto trocado em 3–5 pontos · (c) ela grava trechos e troca o rosto. E **horizontal no vertical** (trilho horizontal dentro do 9:16, padrão) ou 16:9 também. Se ela disser para não perguntar, escolher (a) + horizontal no vertical e dizer no fim.
3. Ler §1, §4, §5, §5b, ALINHAMENTO NO QUADRO, CAPA e §6a da Colagem (repo, branch, tokens de marca, repertório fx.js, voz, regras de design, capa, prévia ao vivo) — não duplicar aqui.
   - A prévia também leva a **Caixa de anotações** (obrigatória em toda prévia): logo abaixo das velocidades, uma caixa "Suas anotações" (textarea) para ela digitar enquanto assiste, com botão **+ Marcar tempo** (insere `[m:ss]` do ponto atual do player) e botão **Copiar** (para colar na conversa). A caixa cresce até ~260 px e depois rola por dentro (`max-height` + `overflow-y:auto`, `resize:vertical`, `box-sizing:border-box`, largura 100%); nunca empurra a página nem cria rolagem lateral. Texto guardado no navegador (localStorage com try/catch, uma chave por reel) para não sumir se a página recarregar.
4. ZONA SEGURA Reels + Stories (skill reel-zona-segura, 4/nov/2026): TEXTO só em x 150-915 e y 268-1680; painel, trilho e imagens podem ir até a borda. Antes do MP4, mostrar a ela os prints com a moldura do Story e do Reel.

## 1. Anatomia (aprendida da REF 01 — pegar a ideia, não copiar o verde)
- **Painel geral** (o "tudão"): grade de marcos ligados por trilhos horizontais tipo mapa de metrô; cada nó = título curto + sticker + etiqueta de data. Abre o reel com o título por cima ("X ANOS EM Y MINUTOS") e a câmera deriva pelo painel em perspectiva leve (3D tilt), depois mergulha no 1º marco.
- **Card de marco**: título grande condensado com textura gasta (letras de tamanhos misturados para dar ritmo), texto curto em itálico leve, ilustração-sticker com borda branca, **trilho horizontal com bolinhas atravessando a tela**, data numa etiqueta de papel rasgado/fita crepe. Fundo chapado com vazamento de luz (holofote), poeira de filme, riscos e **vincos de papel dobrado**.
- **Navegação**: entre marcos o card desliza pelo trilho (dá pra ver o próximo entrando pela lateral); data troca com contador. Marco desconhecido = "????". No kit: componente `.rail` com `.st` (past/on) — ver `preview_kit/gen.py` ("Querida amiga").
- **Dentro do marco nada é fixo**: rosto da época → gráfico → recorte de jornal → clipe de arquivo P&B em tela cheia → volta ao card. Reaproveitar presets da Colagem (`.cnt`, `.bar`, `.webcard`, `.torn`, `data-kb`, `glitch`).
- **Legenda**: **Legenda falada = SEMPRE 2 linhas cheias** (páginas de ~60–64 caracteres em 860 px; nunca 1 linha curta nem palavra sozinha), e só a cor amarela anda palavra por palavra seguindo a voz (tempos reais por palavra). Assim dá pra ler a frase sem esperar palavra por palavra (ela, 19/out/2026). Branca, `.kar.karfull`, centro-baixo, posição e espaçamento do rodapé = Colagem §5b; gráficos seguem a voz = Colagem §5e.
- **Fechamento**: volta ao painel inteiro (o "tudão") com todos os marcos acesos; depois versão vertical do painel rolando de cima a baixo; créditos/fontes em P&B.

## ABA "VÍDEO ORIGINAL" na prévia (vale para todos os formatos de reel, ela 23/out/2026)
Sempre que o reel parte de um vídeo de outra pessoa (link do Instagram, entrevista, fala de político), a prévia ganha uma aba "Vídeo original" com o vídeo inteiro, pra ela assistir e achar outros trechos que valham. Versão leve, feita uma vez só junto com os cortes (no mesmo lugar onde o MP4 já foi baixado, sem gastar outra rodada): `ffmpeg -i orig.mp4 -vf scale=432:768,fps=24 -c:v libx264 -preset slow -crf 32 -g 48 -pix_fmt yuv420p -c:a aac -b:a 64k -ac 1 -movflags +faststart original_leve.mp4` (cerca de 5 MB por 1:30) + pôster jpg. Publicar como arquivo do artifact (não data URI), `<video controls playsinline preload="none">`, sem transcrição nem análise extra. Ao trocar de aba, pausar a trilha da prévia e o vídeo original.

## ALINHAMENTO NO QUADRO — vale para os 3 formatos (Colagem, Timeline, Desabafos), ela 19/out/2026
- **Horizontal:** cada bloco ocupa a largura inteira da área útil, da ponta esquerda à ponta direita da linha de referência (na Colagem/Timeline = trilho `.rail` do topo: `left:60px; width:960px` dentro de `.safe`, gráficos `w=960`; no Desabafos = margem de 116 px dos dois lados). Nada encolhido num canto, nenhuma frase quebrando antes do fim da linha. O TEXTO desses blocos continua dentro da zona segura (x 150-915).
- **Vertical:** o conteúdo da tela se espalha no espaço entre o título do capítulo e a legenda, nunca tudo amontoado em cima com um buraco antes da legenda. Na Colagem/Timeline: `window.VFILL = 1390` (y limite, em coordenadas da cena) liga o `vfill` do `layout.js` — o 1º slot (título do capítulo) fica onde está, a sobra vira espaço extra igual entre os blocos seguintes (até +120 px cada) e o que ainda sobrar desce o corpo, metade em cima e metade embaixo. `data-vfill="0"` desliga numa cena (ex.: cena de gancho com composição própria). Na prévia, o `mkpreview` também precisa pôr `window.VFILL`. No Desabafos: centralizar o bloco de texto no cartão e distribuir as linhas número+frase na altura do quadro.
- Cena com muito texto não tem sobra — tudo bem; o limite continua sendo terminar ≥ 60 px acima da legenda.
- Conferir antes de publicar: quadro do FIM de cada cena (tudo já entrou), checagem de sobreposição/margem zerada e mais baixo conteúdo de cada cena perto do limite (não 300 px acima dele).

## CAPA: obrigatória, feita junto com a 1ª versão (vale para os 3 formatos, ela 19/out/2026)
- A capa nasce quando a 1ª versão do vídeo fica pronta, não no fim. Já entra na prévia (imagem ao lado do player + botão **⬇ Capa** no painel de postagem) e acompanha toda republicação. Nunca postar sem capa: no Metricool vai em `videoThumbnailUrl`.
- O objetivo é CLIQUE, não opinião: um gancho que faça os dois lados quererem abrir (modelo: "Há 20 anos a culpa é da esquerda?", que o vídeo depois desmonta). Pode soar como a pergunta ou acusação que a direita faria; a capa não precisa ser a favor da esquerda nem do tema e nunca entrega o veredito.
- Planejada e personalizada por tema: rosto real de quem está em jogo (recortado, sem fundo, com brilho/cor do tema atrás), uma frase curta e um número ou data GRANDE que todo mundo enxerga no feed. Paleta escolhida pelo tema (ex.: rosa e preto para mulheres), não sempre a mesma.
- Sem fato errado e sem número fora de contexto: todo número da capa está no vídeo e tem fonte.
- Texto dentro da ZONA SEGURA Reels + Stories (skill reel-zona-segura: x 150-915, y 268-1680; imagem e fundo podem ir até a borda; conferir com a moldura do Story e do Reel antes do MP4) e legível na miniatura quadrada do grid (miolo central).
- Quando der, fazer 2 opções e deixar ela escolher na prévia.
- Salvar em `motion/` (capa.jpg) e registrar no STORY doc.

## 2. Realismo e cinema (o que dá a cara "profissional")
- **Luz conta a história**: a cena do apresentador muda de horário conforme a época — dia (início) → fim de tarde → noite com luz prática colorida → **luz vermelha** no momento sombrio (ditadura/censura) → P&B dessaturado num choque. Para avatar: gerar/gradar cada clipe no "horário" do capítulo. Sem apresentador: o fundo dos cards escurece/esquenta por capítulo.
- **Ângulos variados**: aberto grande-angular, médio, close, close extremo de baixo pra cima, câmera na mão com push-in. Cortes secos entre ângulos na mesma fala (jump cut). Barato: gravar a mesma fala em 2 ângulos no celular, ou 1 take 4K + zoom digital como 2º ângulo.
- **Inserts de B-roll** curtos (0,5–1 s): mão na maçaneta em P&B, rua, objetos — abrem capítulos.
- **Cold open** com gancho (clipe de rua/entrevista ou frase forte) e **callback** do mesmo clipe no final.
- Grade de cor quente, leve granulação, sem cara de estúdio.

## 3. Apresentador / avatar (opcional, custo controlado)
- Máx. 3–5 clipes de 3–6 s por reel: abertura, 1–2 viradas de capítulo, fechamento. O resto é voz + painel.
- Rosto: inventado (nunca de pessoa real). Ela grava → troca o rosto no app do Higgsfield (o conector do Claude só importa/lista, não gera) → Claude encaixa com corte, grade e legenda.
- Selo de "conteúdo de IA" do Instagram quando a pessoa na tela for gerada/trocada.
- A REF 01 tem o apresentador em ~50% do tempo — para ela isso é caro; usar como ideia, não como meta.

## 4. Roteiro (60–90 s; série longa pode ter partes)
1. 0–3 s GANCHO (pergunta ou frase que acusa) + cold open.
2. Título sobre o painel geral + câmera derivando ("X anos em Y minutos").
3. 5–9 marcos. Cada marco: data → card (3–5 s) → 1 prova (gráfico/rosto/arquivo, 2–4 s) → volta ao trilho. Algo muda a cada 1,5–3 s.
4. Virada de capítulo com mudança de luz (se houver apresentador) ou mudança de cor de fundo.
5. Fechamento: "tudão" com todos os marcos + ligação com o presente + pergunta para comentar.
6. Truques de roteiro da REF 01: **palavra plantada** no começo ("guarda essa palavra") e paga no fim ligando marcos distantes; **cold open + callback**; citar episódios anteriores da série. Também funciona: **duas vozes** — narrador (Mark) começa uma história, a moça (Athena) interrompe ("não, esse não, esse eles já sabem") e conta a outra; o narrador volta no fim com "só pra caso vocês não saibam".
7. Quando a tela diz que algo mudou ("recua desde 2020", "caiu"), dizer POR QUÊ e QUEM fez (polícia estadual, PF, MP, briga interna), com o governo de cada esfera na época.
Regras de pesquisa, fonte na tela, vocabulário e legenda = as mesmas da Colagem (§2, §5, §5b).

## 5. Produção
- Painel e cards em HTML no motor da Colagem (`engine.js` + `fx.js` + `layout.js` com `window.VFILL`); componente `.rail` (trilho) do kit; `data-cam="x,y,zoom"` por cena para navegar (a implementar e documentar em REPERTORIO.md).
- **Prévia ao vivo como artifact ANTES de qualquer MP4** (Colagem §6a): vídeo inteiro no navegador em tamanho de celular, áudio como relógio, Play/Pausa, barra, botões ↺30s ↺10s ↺5s 5s↻ 10s↻ 30s↻, velocidades 1/1,05/1,1/1,2/1,5/2/3x, caixa de anotações embaixo das velocidades (ver §0.3), aba "Vídeo original" quando houver vídeo-fonte, republicar no mesmo link a cada ajuste e dizer o que mudou. MP4 só depois que ela aprovar. A capa (seção CAPA) já aparece na 1ª prévia.
- Voz, áudio e QA: igual à Colagem §4/§6. REGRA DURA: rascunho SEMPRE com voz grátis da Microsoft (edge-tts: `pt-BR-ThalitaMultilingualNeural` mulher, `pt-BR-AntonioNeural` homem); ElevenLabs só depois que ela aprovar o vídeo inteiro e liberar a voz final, e SEMPRE 1 take só (`generations_count: 1`, nunca repetir a chamada).
- Saída: Drive News › Reels_Shorts › `v<N>_<slug>/` com `motion/`, `resources/` e STORY doc (header → HOW TO USE → BRIEF/RESEARCH → CENA A CENA → LEGENDA → NOTES; revisão = novo NOTE datado).

## 6. Nova referência
Mesmo processo da Colagem §1c: baixar, quadros 5 s + quadros-chave nomeados por cenário + folhas de contato + transcrição → `repertorio/ref_NN_<pagina>/` no Drive (nada de print de terceiros no repo público) → bloco REF NN + NOTE no doc TEMPLATE.