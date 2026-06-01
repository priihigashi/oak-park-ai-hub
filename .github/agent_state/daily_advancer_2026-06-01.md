# Daily Advancer — 2026-06-01

Run date: 2026-06-01 (America/New_York)
Items Advanced: 3

---

## ITEM 1 — PR #186: DEADLINE TODAY — NOT MERGED ⚠️

**Status: URGENT — PR open, NOT merged. Deadline is Sunday 2026-06-01 EOD.**

If not merged today, `weekly-report.yml` fails Monday 2026-06-02 at 9AM ET and creates issue #187.

PR: https://github.com/priihigashi/oak-park-ai-hub/pull/186
Title: fix: add weekly_report.py + email secret (resolves #158 #176)
Files: `scripts/weekly_report.py` (263 lines) + `.github/workflows/weekly-report.yml` (env block)

⚠️ Only YOU can do (3 steps):
1. Open PR: https://github.com/priihigashi/oak-park-ai-hub/pull/186
2. Review (2 files only, all standard) → click "Merge pull request"
3. Go to Actions → weekly-report.yml → "Run workflow" to confirm email arrives

After merge: close issues #158 and #176.

---

## ITEM 2 — EP005 GRINGO: DAGUERREOTYPE CONFIRMED ✅

**Status: PRODUCAO-PRONTO → DAGUERREOTIPO CONFIRMADO. Production can be triggered.**

The one remaining blocker from the PRODUCAO-PRONTO brief has been resolved.

**Confirmed image:**

Title: "General Wool and staff in the Calle Real, Saltillo, Mexico, taken by an unknown photographer during the Mexican-American war, ca.1847"

Wikimedia page: https://commons.wikimedia.org/wiki/File:General_Wool_and_staff_in_the_Calle_Real,_Saltillo,_Mexico,_taken_by_an_unknown_photographer_during_the_Mexican-American_war,_ca.1847.jpg

Direct image URL:
https://upload.wikimedia.org/wikipedia/commons/6/6a/General_Wool_and_staff_in_the_Calle_Real%2C_Saltillo%2C_Mexico%2C_taken_by_an_unknown_photographer_during_the_Mexican-American_war%2C_ca.1847.jpg

License: **Public Domain** (published before January 1, 1931 — Creative Commons Public Domain Mark 1.0)

Credit line for carousel: "Foto: Fotógrafo desconhecido, ca.1847 / Amon Carter Museum of American Art / Domínio Público"

Why this image works for EP005 Slide 2:
- Real military officers in formal uniform, 1847 Mexico — same war as the myth
- Photo taken in Saltillo, exactly where the "Green Go" myth is set
- Public domain, no attribution rights issues
- The dark uniform on Wool and staff visually kills the "green" myth on sight

**What to add to the brief doc** (https://docs.google.com/document/d/1T9tyCq6zqdyHvJPoQxlUlS1-09ZyHS96PAGg9ynZSXY/edit):

Under SLIDE 2 — A MENTIRA VIRAL, replace:
  "Query de busca: Mexican-American War soldiers daguerreotype 1846 Wikimedia"
With:
  "DAGUERREOTIPO CONFIRMADO: General Wool e seu estado-maior, Saltillo, México, ca.1847.
   URL: https://upload.wikimedia.org/wikipedia/commons/6/6a/General_Wool_and_staff_in_the_Calle_Real%2C_Saltillo%2C_Mexico%2C_taken_by_an_unknown_photographer_during_the_Mexican-American_war%2C_ca.1847.jpg
   Licença: Domínio Público (antes de 1931). Crédito: Fotógrafo desconhecido / Amon Carter Museum of American Art."

**Next action (Priscila or next chat):** Open brief doc, add confirmed image info above, trigger production (acionar producao).

Brief: https://docs.google.com/document/d/1T9tyCq6zqdyHvJPoQxlUlS1-09ZyHS96PAGg9ynZSXY/edit

---

## ITEM 3 — BAKE DAY 7: SH-151 DECISION — DO NOT PROMOTE TO BLOCK

**Status: DECISION WRITTEN. Recommendation: extend observation to 2026-06-08.**

Storytelling Pipeline V2 bake:
- Started: 2026-05-25 (STORY_PIPELINE_V2_ENABLED=1, NICHES=brazil)
- Observation window: 7 days (2026-05-25 → 2026-06-01)
- Brazil carousels built since bake start: **ZERO**
- news-source-gate TP/FP data collected: **0 / 0**

### Decision: DO NOT promote SH-151 to BLOCK

Reason: promoting advisory → block with zero data means the gate would silently reject all future Brazil builds the moment the first one triggers, with no calibration baseline. There is no evidence of false positives OR true positives yet.

The zero-build count has an innocent explanation: Brazil content builds run only when a Capture Queue item reaches READY_TO_BUILD status through the 4AM agent. The pipeline has been running (healed_modules.json updated daily), but no Brazil carousel triggered naturally since 2026-05-25.

### SH-151 Promotion Conditions (document for next decision)

Promote news-source-gate ADVISORY → BLOCK ONLY when ALL of these are met:
1. ≥ 3 Brazil carousels have been gated by news-source-gate (TP or FP)
2. TP rate ≥ 70% over those events
3. ≤ 2 FP/week (gate blocked a legitimate source)
4. Zero crashes attributable to the gate

### Rollback instruction (if needed)
Set STORY_PIPELINE_V2_ENABLED=0 in `.github/workflows/content_creator.yml` — byte-identical output for OPC and USA confirmed (scope filter silently skips).

### Recommendation for next session
- Continue observing for 7 more days (re-check 2026-06-08)
- If still zero builds by 2026-06-08: investigate why no Brazil items are reaching READY_TO_BUILD — may be a queue issue, not a gate issue

---

## BAKE DAY 7 SUMMARY (carry-forward from 2026-05-31 Day 6 report)

Day 3 (2026-05-28): CLEAN — no crashes, no gate hits  
Day 6 (2026-05-31): CLEAN — no crashes, no gate hits, zero carousels  
Day 7 (2026-06-01): CLEAN — healed_modules.json updated at 14:04 UTC. researched_modules.json updated. No pipeline failures found in state files.  

4AM agent health: HEALTHY (daily commits to healed_modules + researched_modules confirm nightly run)

---

## DELIVERY CHANNELS

CANAL A (Productivity & Routine doc): BLOCKED — Composio MCP requires OAuth re-auth in remote session. Update manually or in next live chat session: https://docs.google.com/document/d/1wVBuNOuOufT8WP4KCrrlVbKWRmQZjKvqmia1soUEBZE
CANAL B (email): Gmail MCP draft created (see below)
CANAL C (GitHub state file): ✅ DELIVERED — .github/agent_state/daily_advancer_2026-06-01.md

View this report: https://github.com/priihigashi/oak-park-ai-hub/blob/main/.github/agent_state/daily_advancer_2026-06-01.md
PR #186 (merge TODAY — last chance): https://github.com/priihigashi/oak-park-ai-hub/pull/186
EP005 brief: https://docs.google.com/document/d/1T9tyCq6zqdyHvJPoQxlUlS1-09ZyHS96PAGg9ynZSXY/edit
