# Daily Advancer — 2026-05-31

Run date: 2026-05-31 (America/New_York)
Items Advanced: 3

---

## ITEM 1 — WEEKLY REPORT: PR #186 SUBMITTED — MERGE BEFORE SUNDAY EOD

**Status: DONE — PR open, ready to merge.**

Root cause (confirmed by 2026-05-29 advancer): `scripts/weekly_report.py` did not exist.
Previous advancers blocked on Codex route. This run created the PR directly via GitHub MCP.

PR #186: https://github.com/priihigashi/oak-park-ai-hub/pull/186
Branch: fix/weekly-report-script
Files changed:
  - `scripts/weekly_report.py` — 263-line script (draft from 2026-05-29 advancer appendix)
  - `.github/workflows/weekly-report.yml` — added `PRI_OP_GMAIL_APP_PASSWORD` to env block

**DEADLINE: Merge before Sunday 2026-06-01 EOD — next failure Monday 2026-06-02 9AM ET.**

⚠️ Only YOU can do:
1. Open PR: https://github.com/priihigashi/oak-park-ai-hub/pull/186
2. Review changes (2 files, all standard) → click "Merge pull request"
3. After merge: go to Actions → weekly-report.yml → "Run workflow" to test immediately
4. Close issues #158 and #176 once you confirm the email arrives

---

## ITEM 2 — BLOG DUPLICATE BUG: ROOT CAUSE FOUND

**Finding**: Issues #149 (2026-05-14) and #185 (2026-05-31) have the SAME WordPress title: "Commercial Construction Broward: What $82M Means". Two separate posts (ID 6798 and 6845) with identical titles.

**Root cause**: `markSheetRowPosted()` in `scripts/blog-generator.js` wraps the sheet update in try/catch and swallows failures silently. If the sheet write fails after WordPress post creation, the Content Ideas row keeps status "🆕 Idea" + no `blogUrl`, so the NEXT daily run picks the same row again → Claude regenerates the same title.

**Recommended fix** (1-line change in blog-generator.js):
Before calling `generatePost()`, set the row status to "🔄 Processing" in the sheet.
This way, even if the post-write update fails, the row is locked from re-use.

The fix is a code change — route to Codex as a follow-up to PR #186.
File: `scripts/blog-generator.js`, function `getApprovedTopicFromSheet()` → add pre-generation status lock.

**Blog backlog status (as of today)**:
18 WordPress drafts unpublished since May 13 (issues #148–#185 open).
Issue #185 today is the confirmed duplicate of #149.
Recommend: Publish the non-duplicate posts via WordPress admin → https://oakpark-construction.com/wp-admin/edit.php?post_status=draft&post_type=post

---

## ITEM 3 — INSPIRATION LIBRARY: 10 ROWS — CONTENT IDEAS READY TO WRITE

**Status: Ideas drafted — cannot write to sheet in this environment (no Sheets OAuth). Copy-paste to sheet or run via Codex.**

Sheet: https://docs.google.com/spreadsheets/d/1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU

Backlog: ~19 auto-failed rows remain after 2026-05-29 audit. Top 10 with ideas:

**Row 25 | zxtKh82L0kI | Quick Construct | 428k views (HIGHEST PRIORITY)**
G25: Driveway Afundou? O Que Acontece Embaixo do Concreto — Reel 15-30s timelapse de escavação + recompactação de base + nova laje. Hook: "A calçada afunda quando a base falha — não a calçada." Ângulo OPC: antes de reforçar, verifique a base. CTA: "Nós diagnosticamos antes de concretar." AI Score: 5

**Row 28 | L0rxvI0t-TA | Hummel Concrete | 85k views**
G28: Você Pode Colapsar Sua Própria Calçada? — Reel 15-30s ou Carousel 3-4 slides: erros de carga que destroem driveways (veículos pesados, falta de cura, base não compactada). Hook: "Ele destruiu sem perceber." Ângulo OPC: conhecimento gera respeito + CTA inspeção. AI Score: 4

**Row 27 | EASZYToPDOU | Crystel Montenegro | 33k views**
G27: Pérgola de Jardim: O Que Todo DIY Acerta — E O Que Faz Cair em 2 Anos — Carousel 4 slides: fundações de pergolado, materiais vs. calor + umidade da Flórida, código de Broward para estruturas sem permissão. Hook: "Parece simples. Mas em South Florida, o vento e a umidade decidem." AI Score: 3

**Row 21 | EPdb-M8i1K8 | FixNow Studio | 25k views**
G21: De Abandonada para Luxo: O Que Ninguém Mostra no Meio — Carousel 5 slides: estrutura oculta, problemas de fundação, infiltrações escondidas, por que reforma total ≠ obra nova. Hook: "O before/after esconde a parte mais cara." AI Score: 4

**Row 29 | DXYCKjlkWtB | @evolvebuilds | fireplace/masonry**
G29: Lareira do Zero: O Que Exige Profissional em South Florida — Carousel 3-4 slides: código de gás vs. elétrico vs. lenha em Broward, scribing/trim em alvenaria, inspeção e permissão. AI Score: 3

**Row 37 | DXXoRiUkQW3 | @elite__exteriors | pergola + kitchen**
G37: Cozinha Gourmet + Pergolado: O Combo de Maior ROI no Quintal em South Florida — Carousel 4 slides: pergolado com venezianas + ilha gourmet = espaço 365 dias, custo realista, código de Broward para estruturas externas. AI Score: 4

**Row 40 | DXXpjy4oCdV | @deckremodelers | outdoor kitchen island**
G40: Ilha Gourmet no Quintal: O Que Só os Profissionais Faziam Até Ontem — Carousel 4 slides: tendência de ilha gourmet residencial, estrutura amateur vs. profissional, durabilidade em clima úmido. AI Score: 3

**Row 41 | DXXq32_iRoh | @vegasprimeconstruction | outdoor kitchen**
G41: Cozinha Externa: 3 Erros Que Custam o Dobro na Reforma — Carousel 3-4 slides: fundação inadequada, materiais não resistentes à umidade, falta de permissão (Broward exterior structures). AI Score: 3

**Row 31 | DXYE3wbgfHK | @blackwellconstruction.ca | design-build**
G31: Design-Build vs. Contratante + Arquiteto Separados — Carousel 4 slides: diferença de accountability, custo real, tempo, risco. Hook: "Uma decisão que muda todo o seu projeto." AI Score: 3

**Row 30 | DXYE1cZDL0A | @topbuilt.constructions | luxury renovation**
G30: Reforma de Alto Padrão: Onde Está o Dinheiro de Verdade — Carousel 4 slides: o que define "luxo" em construção, onde economizar vs. onde não dá para economizar. AI Score: 3

### HOW TO WRITE THESE TO SHEET
Option A (fastest): Open a new chat → paste this section → say "write these G values to the Inspiration Library sheet."
Option B: Open new chat Codex → paste row numbers + G values → script writes via Sheets API.

---

## BAKE DAY 6 STATUS — NO BRAZIL BUILDS YET

STORY_PIPELINE_V2_ENABLED=1, NICHES=brazil active since 2026-05-25.
6 days into 5-7 day observation window.
Zero Brazil carousels built since bake start — gate metrics still 0/0.
Bake window ends ~2026-06-01. First TP/FP measurement will happen when next Brazil carousel is triggered.
Action: On 2026-06-01, check if SH-151 BLOCK promotion should proceed (news-source-gate advisory → block).

---

## DELIVERY CHANNELS

CANAL A (Productivity & Routine doc): BLOCKED — Composio MCP requires OAuth re-auth in remote environment.
CANAL B (email): Gmail MCP draft created (see below).
CANAL C (GitHub state file): ✅ DELIVERED — .github/agent_state/daily_advancer_2026-05-31.md

View this report: https://github.com/priihigashi/oak-park-ai-hub/blob/main/.github/agent_state/daily_advancer_2026-05-31.md
Productivity & Routine doc (update manually or next session): https://docs.google.com/document/d/1wVBuNOuOufT8WP4KCrrlVbKWRmQZjKvqmia1soUEBZE
PR #186 (merge before Sunday): https://github.com/priihigashi/oak-park-ai-hub/pull/186
