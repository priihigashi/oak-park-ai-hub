# Daily Advancer — 2026-06-21

Run date: 2026-06-21 (America/New_York)
Items Advanced: 3 (research + docs created)
Blocked: Composio Google Docs INACTIVE — could not write to EP005, EP007, or Productivity & Routine doc

---

## ITEM 1 — PIPELINE FAILURE CONFIRMED: content_creator run 27821993206 (June 19)

Status: FINDING — requires Priscila decision on REVIEW_STRICT behavior

### What happened:
- content_creator.yml ran on schedule 2026-06-19 at 6:30 AM UTC
- Run ID: 27821993206 — FAILED
- Failure stage: "Run carousel reviewer" step
- Root cause: `scripts/content_creator/carousel_reviewer.py` exits with code 1 when REVIEW_STRICT=true
  AND the reviewer finds quality issues. REVIEW_STRICT defaults to 'true' in the workflow.
- Result: Step 13 "Send Preview Emails" was SKIPPED. Priscila received a failure ALERT
  email (step 16 fired) but NO content preview email was sent.

### ads_pulse.yml "bug" from 2026-06-15 session — CONFIRMED NOT A BUG (same finding as 2026-06-17):
- Line 48 maps `GMAIL_APP_PASSWORD` env var → `secrets.PRI_OP_GMAIL_APP_PASSWORD` (correct)
- Python reads `os.environ['GMAIL_APP_PASSWORD']` (correct — matches env var name in step scope)
- No code change needed. Remove from carry-forwards.

### Next pipeline run: 2026-06-22 at 6:30 AM UTC
- If reviewer still finds issues, it will fail again and preview emails will be skipped again
- Decision needed: Should REVIEW_STRICT default be changed to 'false' for scheduled runs,
  and only 'true' for manual workflow_dispatch? This would let content flow through with
  warnings instead of hard-stopping the pipeline.

---

## ITEM 2 — EP005 GRINGO: DAGUERREOTIPO CONFIRMADO, PRODUCAO DESBLOQUEADA

Status: DONE (research) — needs Priscila to update EP005 doc and trigger production

### Confirmed public domain image:
- File: "Daguerreotype of the Mexican American War ca 1847 1848.jpg"
- URL: https://upload.wikimedia.org/wikipedia/commons/b/b2/Daguerreotype_of_the_Mexican_American_War_ca_1847_1848.jpg
- Wikimedia page: https://commons.wikimedia.org/wiki/File:Daguerreotype_of_the_Mexican_American_War_ca_1847_1848.jpg
- License: Public Domain (CC Public Domain Mark 1.0) — NO attribution required
- Source: Beinecke Rare Book & Manuscript Library, Yale University
- Content: Virginia regiment and Webster's battalion in Saltillo, Mexico, circa 1847-1848
- Uniform colors: dark/blue — visually destroys the "Green Go" myth (no green uniforms)

### Previous false candidate (rejected):
- File:US_and_mexican_soldiers_1846-1848.jpg — was CC BY-SA 2.0, modern reconstruction, NOT real daguerreotype

### EP005 doc (1T9tyCq6zqdyHvJPoQxlUlS1-09ZyHS96PAGg9ynZSXY):
- Status was PRODUCAO-PRONTO with one blocker: confirm daguerreotype
- BLOCKER NOW CLEARED — production can be triggered immediately
- NOTE: Could not prepend daguerreotype confirmation to the doc (Composio inactive this session)
- Action: Next session, update EP005 doc with image URL above, then trigger build

---

## ITEM 3 — EP007 BÍBLIA: DOC CREATED, BRIEF PREPARED (NOT YET WRITTEN)

Status: PARTIAL — doc shell created, brief content ready, write blocked by Composio

### Doc created:
- Title: "EP007 — BÍBLIA — Production Brief"
- Google Doc ID: 1hag0h3ly5SJ_awhztbUpL6IE29erBLCiAnlVniDxwUc
- Currently EMPTY — Composio googledocs was inactive, could not write content

### FULL BRIEF (write this to the doc in next session):

SERIE: Defesa Etimológica — EP007
FORMATO: FORMAT-024 (Brazil etymology debunk carousel)
FALSA CRENÇA: BÍBLIA = "Básica Instrução Antes de Largar o Inferno" (viral no WhatsApp)
VERDADE: A palavra "bíblia" vem do grego "ta biblia" (os livros/os escritos)

ETIMOLOGIA COMPLETA:
1. Byblos — cidade fenícia (hoje Líbano) que exportava papiro pelo porto para o Mediterrâneo
2. Grego "byblos" = papiro (material de escrita exportado por Byblos)
3. Grego "biblion" = rolo/livro (diminutivo de byblos)
4. Grego "ta biblia" = os livros (plural neutro — coletânea de escritos)
5. Latim "biblia" (sg. feminino) → Português "bíblia"
→ Bíblia = "os livros" — não é sigla, nunca foi sigla

CONTEXTO VIRAL: Acronym backronyms (siglas inventadas retroativamente) são comuns em PT-BR no WhatsApp.
Outros exemplos: AMOR = "Ato de Morrer Outra vez de Ressaca" etc.
A versão fake circula há décadas; a etimologia real é verificável em qualquer dicionário.

ESTRUTURA — 5 SLIDES:
SLIDE 1 — COVER
  Título: "BÍBLIA não é sigla. Nunca foi."
  Subtexto: A palavra mais antiga mal-interpretada do WhatsApp
  Visual: papiro antigo ou mapa do Mediterrâneo + porto de Byblos
  Tag: Defesa Etimológica • EP007

SLIDE 2 — A MENTIRA VIRAL
  Formato: card de WhatsApp (print ou mockup estilizado)
  Texto do card: "BÍBLIA = Básica Instrução Antes de Largar o Inferno 🙏"
  Legenda abaixo: "Seu tio mandou isso hoje. Seu avô vai mandar amanhã."
  Visual: bolha de chat do WhatsApp

SLIDE 3 — O PROBLEMA
  Linha do tempo horizontal:
  → Séc. XI a.C.: Cidade fenícia de Byblos exporta papiro
  → Séc. V a.C.: Gregos chamam o material de "byblos"
  → Séc. III a.C.: LXX usa "ta biblia" para a coleção sagrada
  → Séc. IV d.C.: Jerônimo traduz para o latim → "biblia"
  → Português: "bíblia" — ainda os livros, não sigla
  Visual: timeline simples com ícones (porto → rolo → livro → português)

SLIDE 4 — A ORIGEM REAL
  Mapa simples: Mediterrâneo Oriental + ponto "Byblos (Líbano)" + seta → Grécia → Roma → Portugal
  Texto âncora: "Uma cidade. Um material. Um porto. Uma palavra que atravessou 3.000 anos."
  Rodapé: "Etymonline · Houaiss · Wikipedia: Bible etymology"

SLIDE 5 — CTA
  "Toda sigla tem uma origem. BÍBLIA tem uma cidade."
  "Salva e manda pro seu tio 📲"
  Hashtags: #DefesaEtimológica #Bíblia #EtimologiaPortuguesa #NãoÉSigla #CuriositadesBíblicas
  Fontes no rodapé: Etymonline, Houaiss, Wikipedia (Bible), Wikipedia (Byblos), Ciberdúvidas

CAPTION (legenda do post):
"Seu tio mandou aquela mensagem de BÍBLIA = 'Básica Instrução...' de novo?
A palavra não é sigla. É uma cidade fenícia de 3.000 anos atrás.
Byblos exportava papiro. Os gregos chamaram o material de byblos. Os livros sagrados viraram 'ta biblia'.
Latim → bíblia → você.
Não existe era medieval criando siglas em grego. Passa pra frente a versão certa."

FONTE PINADA:
"📌 Fontes verificadas: Etymonline (bible), Houaiss, Wikipedia — Bible / Byblos, Ciberdúvidas"

CHECKLIST DE PRODUÇÃO:
[ ] Wikimedia Commons: foto/mapa de Byblos (ex: "Byblos port Lebanon" — verificar licença CC)
[ ] Mockup de bolha WhatsApp para Slide 2
[ ] Timeline SVG para Slide 3
[ ] Mapa Mediterrâneo para Slide 4
[ ] build-carousels.yml dispatch com niche=brazil, slug=ep007-biblia

EPISODIOS RELACIONADOS: EP005 (GRINGO), EP006 (JESUS), EP008 (próximo — AMOR sugerido)

---

## DELIVERY STATUS — 2026-06-21

Email: Triggered via GitHub Actions send_email.yml (see email run)
Productivity doc (1wVBuNOuOufT8WP4KCrrlVbKWRmQZjKvqmia1soUEBZE): BLOCKED — Composio googledocs inactive
EP005 doc (1T9tyCq6zqdyHvJPoQxlUlS1-09ZyHS96PAGg9ynZSXY): BLOCKED — Composio googledocs inactive
EP007 doc (1hag0h3ly5SJ_awhztbUpL6IE29erBLCiAnlVniDxwUc): BLOCKED — Composio googledocs inactive

## WHAT PRISCILA NEEDS TO DO

1. DECIDE: Should `REVIEW_STRICT` default to `false` for scheduled content_creator runs?
   → If YES: edit `.github/workflows/content_creator.yml` — change `|| 'true'` to `|| 'false'`
   → Next run is June 22 at 6:30 AM UTC — decide before then

2. EP005 GRINGO: Trigger production (image confirmed, no more blockers)
   → Tell Claude: "EP005 GRINGO — trigger production" in next session

3. EP007 BÍBLIA: Next session, write the brief above to the doc
   → Tell Claude: "Write EP007 brief from agent state 2026-06-21" in next session

## CARRY-FORWARDS (unchanged from 2026-06-17)

- OPC Ads: Build Local/LSA (471) + Billing tabs (approved, code task)
- OPC Ads: Fix OAuth refresh token (Priscila must reauth as mcfollingproperties@gmail.com)
- OPC PM Tool: Mike live test = Phase 1 gate (still pending)
- Brazil carousels: EP005 UNBLOCKED, EP006 JESUS READY, NWS-452 TAXACAO READY
- EP007 BÍBLIA: doc created, brief ready, needs write + build trigger
- Flávio x Vorcaro: research done (2026-06-17), needs build trigger
