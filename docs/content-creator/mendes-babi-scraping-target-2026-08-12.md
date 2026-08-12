# @mendes__babi — Scraping Target Spec
Daily Advancer — 2026-08-12

Priscila added @mendes__babi to the Inspiration Library today with the following note:
"fake news tracking (rastreia fake news). Babi Mendes, 1.8M followers, PUBLIC + verified.
Bio: 'Candidata a Dep. Federal por SP', far-right BR political content (Bolsonaro-aligned memes,
clips, commentary). Scrapeable. Same debunk treatment as @marceloem23 (FORMAT-024 Verdade Pela
Metade): pick highest-performing posts each week, run debunk flow."

---

## What needs to happen

Add one new row to the **🎯 Scraping Targets** tab in Ideas & Inbox
(spreadsheet ID: 1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU).

---

## Exact row to add

The tab structure (read by sheets_writer.py `read_scraping_targets()`):

```
Column A (TYPE/TARGET) | [niche columns, e.g. BRAZIL] | NOTES | DESTINATION
```

New row:

Column A: ACCOUNT
Brazil niche column: @mendes__babi
NOTES: Babi Mendes — Candidata a Dep. Federal por SP. 1.8M followers. Far-right BR political
content, Bolsonaro-aligned. Format: FORMAT-024 Verdade Pela Metade debunk flow (same as
@marceloem23). Pick highest-performing posts each week. Public + verified account.
DESTINATION: Inspiration Library — Brazil News / Debunk Tracking

---

## Why this matters

FORMAT-024 (Verdade Pela Metade) is the debunk-in-kind format: take a viral far-right claim,
verify it, and show what was left out. @mendes__babi is a high-volume source (1.8M followers)
of exactly the content FORMAT-024 targets. Adding her alongside @marceloem23 doubles the
weekly claim supply for the debunk pipeline.

---

## Action needed (Priscila or next Claude session)

1. Open Ideas & Inbox → 🎯 Scraping Targets tab.
2. Add the row above in the correct format (matching existing @marceloem23 row).
3. Confirm the APIFY_API_KEY secret in GitHub Actions is active (it was active as of June 2026;
   verify it hasn't expired). Run path: scripts/4am_agent/scraper.py → scrape_all_targets().
4. On next 4AM agent run (4am_agent.yml), the account will be scraped automatically.

---

## Reference — @marceloem23 entry (existing)

Confirm the existing @marceloem23 row's exact column layout before adding @mendes__babi,
so the format matches exactly. The sheets_writer.py reads the tab as a header matrix, so
the niche column name must match the existing header row exactly.
