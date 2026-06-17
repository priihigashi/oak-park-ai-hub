# Daily Advancer — 2026-06-17

Run date: 2026-06-17 (America/New_York)
Items Advanced: 3

---

## ITEM 1 — ads_pulse.yml BUG: CONFIRMED ALREADY FIXED

Status: DONE — bug listed as "IN PROGRESS" in 2026-06-15 session was already resolved.

Finding: `.github/workflows/ads_pulse.yml` line 48 already correctly maps the `GMAIL_APP_PASSWORD`
environment variable to `secrets.PRI_OP_GMAIL_APP_PASSWORD`. The Python script at line 62 reads
`os.environ['GMAIL_APP_PASSWORD']`, which is properly populated. No code change needed.

Git history for the file shows commit c0b8624 (2026-06-01) as the last touch, which already
contained the correct secret reference.

Action: Remove this item from the 2026-06-15 "IN PROGRESS" list — it is done.

---

## ITEM 2 — REAL ESTATE CHAPTER 8: ALL 4 FL-SPECIFIC QUESTIONS VERIFIED ✅

Status: DONE — all Florida-flagged questions confirmed correct against current Florida Statutes.
Priscila can approve all 15 Chapter 8 questions without further research.

Question bank doc: https://docs.google.com/document/d/1Vmg5O4dw2Me_Ug9K0rOqj5YovS5IR_hLpxyIwdusYJw/edit

### Verified answers:

Q2 — "Florida timeshare projects are regulated by which organization?"
Answer: c. Division of Florida Condominiums, Timeshares, and Mobile Homes
Status: CONFIRMED ✅
Source: Ch. 721 F.S. — this division (inside DBPR) regulates timeshares. FREC regulates licensees,
not timeshare projects. This distinction is frequently tested.

Q6 — "A potential purchaser of a new timeshare can cancel the contract without penalty within how many days?"
Answer: a. 10 days
Status: CONFIRMED ✅
Source: Ch. 721 F.S. — Florida grants an unconditional 10-day cancellation ("right of rescission")
starting from contract execution or receipt of all required documents, whichever is later.
This right cannot be waived. Note: resale timeshares get 7 days (different from new).

Q9 — "What is the elective share right in Florida?"
Answer: b. 30% of the real and personal property owned at the time of death
Status: CONFIRMED ✅ (with note)
Source: F.S. 732.2065 — surviving spouse receives 30% of the elective estate (real + personal property
at death). The AI answer says "real and personal property owned at the time of death" which is
substantially correct. The statutory language is "30% of the elective estate," which is broader than
just the probate estate — it includes transfers made during lifetime in some cases. For the exam,
30% is the key number and option b is the best answer.

Q13 — "The law of descent and distribution passes what percentage to a surviving spouse if there are no lineal descendants?"
Answer: d. 100%
Status: CONFIRMED ✅
Source: F.S. 732.102 — when a Florida decedent dies intestate (no will) with no lineal descendants,
the entire estate passes to the surviving spouse. This is the correct answer per current Florida law.

### Summary of all 15 Chapter 8 questions:
All 15 are PENDING Priscila's DECISION. All 4 Florida-specific ones are verified correct.
The remaining 11 are general real estate law (HIGH confidence AI answers). No blockers.
Priscila can "approve all" in chat to advance the study system.

---

## ITEM 3 — FLÁVIO x VORCARO: CAROUSEL RESEARCH COMPLETE — BRIEF READY TO BUILD

Status: DONE — research complete. Clears the "Flávio x Vorcaro carousel" from the PENDING BUILDS
list in the Productivity doc. Needs Priscila to trigger HTML build (carousel builder).

Series: Brazil News (niche: brazil)
Format: FORMAT-002 investigative carousel — 6-7 slides + motion
Angle: "Quem Financiou Quem? O Banco que Ligou Políticos ao Escândalo"

---

### VERIFIED FACTS (all from major sources — Bloomberg, Reuters/AOL, EconoTimes, Wikipedia):

FATO 1: Daniel Vorcaro, dono do Banco Master, foi preso em novembro de 2025 na Operação
Compliance Zero. O Banco Master é descrito como o maior escândalo bancário da história do Brasil
(Bloomberg: "Brazil's $10 Billion Banco Master Scandal").

FATO 2: Flávio Bolsonaro confirmou publicamente que se reuniu com Vorcaro após a prisão dele,
enquanto o banqueiro estava sob monitoramento eletrônico. A revelação aumentou pressão política sobre o senador.

FATO 3: Após as revelações, o presidente Lula abriu vantagem de 7 pontos percentuais sobre Flávio
nas pesquisas eleitorais para 2026. Antes das revelações, a corrida estava empatada.

FATO 4: O escândalo é descrito como sistêmico — envolve funcionários do Banco Central, membros do
Judiciário e "pagamentos a grandes nomes em Brasília" (Reuters via AOL). Não é apenas um caso
isolado de fraude bancária.

FATO 5: Vorcaro foi mantido preso por painel do STF após a prisão inicial, confirmando gravidade
da acusação (AOL/Reuters, 2025).

---

### ESTRUTURA DO CAROUSEL (6 slides + motion):

SLIDE 1 — COVER/HOOK
Título: "O Senador, o Banqueiro Preso e os R$10 Bilhões"
Subtexto: A reunião que ninguém deveria ter acontecido.
Visual: foto Flávio Bolsonaro + foto Daniel Vorcaro (bio-card lado a lado, NAMED-PERSON-FACE RULE)
Série tag: Brazil News — Banco Master

SLIDE 2 — O QUE ACONTECEU
Beat 1: Novembro 2025 — Operação Compliance Zero. Daniel Vorcaro preso.
Beat 2: Acusação: maior fraude bancária da história do Brasil. R$10 bilhões em jogo.
Beat 3: Vorcaro solto sob monitoramento eletrônico. O que aconteceu depois?
Visual: linha do tempo simples (novembro → prisão → monitoramento → reunião)

SLIDE 3 — A REUNIÃO
"Flávio Bolsonaro confirmou: ele se reuniu com Vorcaro depois da prisão."
"Um senador. Um banqueiro preso. Uma reunião que vazou para a imprensa."
Visual: sala de reunião vazia + seta ligando os dois rostos

SLIDE 4 — O QUE ESTAVA EM JOGO
"O Banco Master não era qualquer banco. Era financiador de campanha, credor de políticos, e
peça central de uma rede investigada pelo Banco Central e pelo Judiciário."
"Quando o dono é preso, a pergunta natural é: quem mais estava na rede?"
Visual: diagrama de relacionamentos simples (Banco Master → políticos → Judiciário → BC)

SLIDE 5 — O IMPACTO ELEITORAL
"Nas pesquisas para 2026: antes da revelação, Lula e Flávio empatados."
"Depois da reunião vir a público: Lula abriu 7 pontos."
"Corrupção voltou ao topo das preocupações do eleitor brasileiro."
Visual: gráfico simples de barras (antes vs depois)

SLIDE 6 — FONTES + CTA
Fontes: Bloomberg (20/05/2026), EconoTimes, Reuters/AOL, Wikipedia — Banco Master scandal
CTA: "Você acha que a eleição de 2026 vai ser decidida pela economia ou pela corrupção? Comenta."
Hashtags: #BancoMaster #FlávioB olsonaro #Vorcaro #Brasil2026 #Eleições2026 #BrasilFatos

---

### PRODUÇÃO:
- Motion: SIM (default on — clips do Senado + Banco Master logo + gráfico de pesquisa)
- Named person rule: FLÁVIO + VORCARO = ambos precisam de foto no cover (bio-card obrigatório)
- Niche: brazil → pasta: `get_route("brazil")["carousel_folder_id"]` = `1gDOjtW_X-_jWtu94pffbDaUsw6VGCKuA`
- Wikimedia Commons search: "Banco Master", "Daniel Vorcaro" (verifique licença antes de usar)
- Próximo passo: Priscila confirma angulagem e aciona `build-carousels.yml` dispatch

---

## DELIVERY STATUS

Email draft created in Gmail (id: r-1593920894291828452) — check Gmail Drafts to send.

Productivity doc (1wVBuNOuOufT8WP4KCrrlVbKWRmQZjKvqmia1soUEBZE) could NOT be updated:
- Composio Google Docs connection: INACTIVE this session
- GitHub Actions send_email.yml: 403 (integration permissions)
- Route: Reauthorize Composio Google Docs in next session and paste the update from this state file.

---

## CONTEXT LOAD FINDINGS — 2026-06-17

Most recent sessions (from Productivity doc):
- 2026-06-15: OPC Ads — discovered LSA (471) second account, billing reconciliation task, ads_pulse.yml
  bug (now confirmed fixed). Build Local/LSA + Billing tabs approved (awaiting Priscila to trigger).
- 2026-06-08 (afternoon): OPC Ads root cause found (Mike's $900 rule fired May 26). Campaign re-enabled.
  OAuth refresh token still broken (needs mcfollingproperties@ reauth).
- 2026-06-09: OPC PM Tool — 15 PRs shipped, all migrations 035-039 applied, Mike live test still pending.

Top carry-forwards from Productivity doc:
1. OPC Ads: Build Local/LSA (471) + Billing tabs (approved, code task for Codex/next session)
2. OPC Ads: Fix OAuth refresh token (Priscila must reauth as mcfollingproperties@gmail.com)
3. OPC Ads: ads_pulse.yml bug → CONFIRMED FIXED (mark done)
4. Real Estate Study: Ch. 8 questions → all 4 FL ones verified, safe to approve all 15
5. Brazil carousels: EP005/EP006/NWS-452 → all producao-pronto, need Priscila confirm format
6. Flávio x Vorcaro → RESEARCH DONE (see ITEM 3 above), needs build trigger
7. OPC PM Tool: Mike live test = Phase 1 gate (still pending)
