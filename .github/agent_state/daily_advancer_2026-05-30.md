# Daily Advancer — 2026-05-30

Run date: 2026-05-30 (America/New_York)
Items Advanced: 3

---

## ITEM 1 — BLOG DRAFT BACKLOG: 17 DRAFTS UNPUBLISHED SINCE MAY 13

**Finding**: The blog pipeline (blog-generator.js) has been running daily and creating WordPress drafts. Zero posts have been published since May 13 — 18 days of SEO content sitting idle. At current rate, this grows by 1/day.

**Open WordPress issues (oldest → newest, publish in this order):**

PRIORITY 1 — PUBLISH NOW (≥2 weeks old, highest SEO urgency):
- #148 (2026-05-13): "Concrete Slab Preparation: Avoid DIY Fails" → https://oakpark-construction.com/wp-admin/post.php?post=6795&action=edit
- #149 (2026-05-14): "Commercial Construction Broward: What $82M Means" → post=6798
- #150 (2026-05-15): "Florida Brownfield Development: What Contractors Need" → post=6801
- #153 (2026-05-16): "Residential Additions Fort Lauderdale: Full Guide" → post=6804
- #155 (2026-05-17): "Contractor Broward County FL: How to Choose Wisely" → post=6807
- #159 (2026-05-18): "How to Choose Home Renovation Contractors Fort Lauderdale" → post=6810
- #160 (2026-05-19): "Concrete Contractor Fort Lauderdale: Your Complete Guide" → post=6813

PRIORITY 2 — PUBLISH THIS WEEK (1–2 weeks old):
- #171 (2026-05-20): "Concrete Services South Florida: What to Know" → post=6816
- #172 (2026-05-21): "Concrete Company Plantation FL: Finish Guide" → post=6818
- #173 (2026-05-22): "Home Flip Renovation South Florida: Real Costs & Timelines" → post=6821
- #174 (2026-05-23): "Manufactured Homes vs Site-Built: Florida Guide" → post=6824
- #175 (2026-05-24): "Home Addition Cost South Florida: Real Breakdown" → post=6827
- #177 (2026-05-25): "Construction Workforce Disruptions: How to Protect Projects" → post=6830

PRIORITY 3 — PUBLISH SOON (<1 week old):
- #181 (2026-05-26): "Patio Paver Installation South Florida: DIY vs. Contractor" → post=6833
- #182 (2026-05-27): "Concrete Slab Contractors: Why DIY Fails in Florida" → post=6836
- #183 (2026-05-28): "Concrete Pouring Mistakes South Florida: Avoid Costly Errors" → post=6839
- #184 (2026-05-30): "South Florida Real Estate Construction Demand: What It Means" → post=6842

**Topic clusters**: 7 concrete/slab posts, 4 renovation/addition posts, 3 FL market/business posts, 3 contractor/general posts.

⚠️ Only YOU can do:
1. Open WordPress: https://oakpark-construction.com/wp-admin/edit.php?post_status=draft&post_type=post
2. Publish posts starting with #148 (oldest first). Review title/content — pipeline auto-generates SEO copy.
3. Close each GitHub issue after confirming published.
Batch publish estimate: 5–7 min total if titles/content are acceptable as-is.

**System note**: Once any 1 post is published, close the corresponding issue to track progress. After clearing the backlog, recommend a future workflow: auto-publish if content quality score ≥ threshold (or set a weekly publish day as a calendar event).

---

## ITEM 2 — PRODUCTION TRIGGER SHEET: 4 CONTENT ITEMS PRONTO PARA PRODUÇÃO

All 4 items have verified briefs. Status + exact next action per item:

### EP005 GRINGO — TRIGGER-READY ✅
Brief: https://docs.google.com/document/d/1T9tyCq6zqdyHvJPoQxlUlS1-09ZyHS96PAGg9ynZSXY/edit
Format: Carousel 5 slides + motion (confirmed 2026-05-20)
Visual Slide 2: daguerreotipo Wikimedia Commons 1846-1848 Public Domain (confirmed 2026-05-27 Advancer)
Status: ZERO blockers remaining.
TRIGGER: Open new chat → "Run content_creator.yml for EP005 GRINGO carousel — brief at [link above]. Niche: brazil."

### EP006 JESUS — ONE DECISION NEEDED
Brief: https://docs.google.com/document/d/1d7296XtAFNtNlQdSDmxnmxPeoJGsfeMyVQd1F77UiB4/edit
VERSION E (Je + sus = porco/cavalo) confirmed as the most viral PT-BR version (2025-2026).
BLOCKER: Format decision only — carousel or reel?
⚠️ Only YOU can do: Reply "carousel" or "reel" in any chat → then say "acionar EP006" → done.

### NWS-452 TAXAÇÃO SUPER-RICOS/LULA — TRIGGER-READY ✅
Brief: https://docs.google.com/document/d/1EikIitjDSqZMvpBvcDAq3QdIKyzJN1PIsB9ZKO9q_U4/edit
6 slides fully written with PT-BR copy. All 4 sources verified (Agência Brasil, IMF, Wikipedia ISF, IBGE PNAD 2024).
Hook B confirmed: "Por que marxistas e liberais de repente concordam sobre taxar os ricos?"
No political figures' faces required (angle is the debate, not Lula specifically).
TRIGGER: Open new chat → "Build NWS-452 carousel — brief at [link above]. Niche: brazil."

### BRAZIL FAKE NEWS EP1 (DADOS SELECIONADOS) — ONE DECISION NEEDED
Brief: https://docs.google.com/document/d/1_3IfM4ijo2Gx7iXXPcKfFLm1zaeilJ2mGoK3Ieb1tpM/edit
Copy final (Exemplo 3 — Homicídios Ocultos) written and appended 2026-05-23.
BLOCKER: Priscila confirms Exemplo 3 is the selected angle.
⚠️ Only YOU can do: Say "confirmo Exemplo 3" in any chat → then say "acionar build HTML" → done.

### BONUS: Tucker/Mendel carousel — draft in .github/agent_state/daily_advancer_2026-05-29.md
Full 7-slide spec + 7 verified sources already written by yesterday's Advancer.
Only needs: (1) Create editorial log doc, (2) confirm FORMAT-024 or FORMAT-002, (3) trigger build.

---

## ITEM 3 — OPC PM TOOL T-N00: DRIVE AUDIT COMPLETE — 4 QUESTIONS ANSWERED

T-N00 in BACKLOG: "Validate Drive folder pattern against actual OPC New Construction shared drive structure."

Audited Drive folder: New Construction (ID: 1ls3ot_l_nuXYl1rVvmYcwK8c2Cr22FdU)

**ACTUAL CURRENT STRUCTURE (confirmed from Drive):**
```
New Construction/
  9720 sw 92nd ter/          ← ADDRESS format, no subfolders, photos dumped directly
    IMG_7714.jpeg, IMG_7571.jpeg, ...
  528 ne 8th ave , Victoria Park/  ← ADDRESS format
  122 Dockside Cir/               ← ADDRESS format
  1270 Harbor Ct/                 ← ADDRESS format
  Kinney Build/                   ← CLIENT NAME exception (no street address)
  General Photos/                 ← general bucket, not a project
```

**ANSWERS TO T-N00 4 QUESTIONS:**

Q1 — Folder naming: code or address?
ANSWER (from Drive): Currently ADDRESS (e.g., "9720 sw 92nd ter", "122 Dockside Cir"). Recommend: continue with address field from projects table to match existing convention. Project code should NOT replace address as folder name — team searches by address, not code. If you want sort order, use address only (alphabetical sort is fine for <20 projects).

Q2 — Project codes unique enough to use as folder identifiers?
ANSWER: Cannot confirm from Drive (Drive doesn't use codes at all). But recommendation above makes this moot: use address as folder name, not code.

Q3 — Receipts/ subfolder OK?
ANSWER (from Drive): Current project folders have NO subfolders — photos are dumped directly. Adding Receipts/ as a new subfolder is SAFE and ADDITIVE — it won't break the existing structure. Current photos would remain loose in the project root; new receipts would go into Receipts/.

Q4 — Should filename include project code?
ANSWER: Not needed if folder = address (project is implied by location). Filename `YYYY-MM-DD_<vendor>_<amount>.<ext>` is sufficient. If you want extra safety (e.g., receipt accidentally moved), add address abbreviation: `YYYY-MM-DD_<vendor>_<amount>_<short-address>.<ext>` — but this is optional.

**RECOMMENDED WRITE-UP FOR CODEX (copy-paste into Codex chat):**
"For T-N04 Drive upload Edge Function: Folder = projects.address field (URL-slug format, lowercase, spaces→hyphens). Example: '9720-sw-92nd-ter'. Subfolder = 'Receipts'. Filename = YYYY-MM-DD_<vendor-slug>_<amount>.<ext>. Auto-create folder + subfolder if missing. No project code in folder name or filename."

⚠️ Priscila must confirm Q4 only if you prefer project code in filename. Otherwise Codex can proceed with the above spec.

---

## BAKE DAY 5 STATUS — CLEAN (no Brazil builds triggered yet)

STORY_PIPELINE_V2_ENABLED=1, NICHES=brazil active since 2026-05-25.
Brazil Drive audit: most recent carousel build = 2026-05-18 (pre-bake). No new Brazil carousel since bake started.
Status: Gates are live but no Brazil content has been triggered in the build queue since bake start.
Gate metrics: 0/0 (no data yet — first measurement will come when next Brazil carousel builds).
4AM agent: running cleanly (commits 98b34fe, 30fb7a3, 8fdc01b, d7191f8 + today's nonnegotiables_updater b3d122d).
New auto-skill from yesterday: SKILL_handle_apify_no_data.md (3-retry logic for Apify NoneType errors).
Next milestone: When first Brazil carousel builds post-bake, check review email for [face-gate], [cadence-gate], [motion-static-gate] tags.

---

## WEEKLY REPORT FIX — STILL PENDING CODEX PR (from 2026-05-29)

Root cause confirmed: scripts/weekly_report.py does NOT exist. Full 263-line script drafted in daily_advancer_2026-05-29.md ITEM 3 APPENDIX.
Next Monday (2026-06-02) 9AM ET: weekly-report.yml will fail AGAIN unless PR is merged before then.
Deadline: Codex PR must be open by EOD Sunday 2026-06-01.

⚠️ Only YOU can do: Open Codex chat → paste: "Create scripts/weekly_report.py using the draft in .github/agent_state/daily_advancer_2026-05-29.md ITEM 3 APPENDIX. Also add PRI_OP_GMAIL_APP_PASSWORD: ${{ secrets.PRI_OP_GMAIL_APP_PASSWORD }} to the env block in .github/workflows/weekly-report.yml. Submit as PR." → Approve PR.

---

## DELIVERY CHANNELS

CANAL A (Productivity & Routine doc): BLOCKED — Composio MCP requires OAuth user auth in remote environment.
CANAL B (email): Gmail MCP draft created → Draft ID logged below.
CANAL C (GitHub state file): ✅ DELIVERED — .github/agent_state/daily_advancer_2026-05-30.md

View this report: https://github.com/priihigashi/oak-park-ai-hub/blob/main/.github/agent_state/daily_advancer_2026-05-30.md
Productivity & Routine doc (update manually): https://docs.google.com/document/d/1wVBuNOuOufT8WP4KCrrlVbKWRmQZjKvqmia1soUEBZE
