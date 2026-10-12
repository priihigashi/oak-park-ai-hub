# Repertório de movimento — Colagem Jornalística

Cada vídeo de referência que a Priih manda vira uma entrada aqui: **o que ele faz em movimento** (não só o quadro parado), **qual preset do motor reproduz isso** e **quando usar**.
Imagens/quadros de referência ficam no Drive (repo é público — nada de print de outra página aqui):
Drive › Videos › `colagem-reel-template` › `repertorio/ref_NN_<pagina>/`.

Demo renderizado de cada entrada: `repertorio.html` → `node capture.js demo.mp4 repertorio.html` + `python3 audio.py events.json a.wav 30`.

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
