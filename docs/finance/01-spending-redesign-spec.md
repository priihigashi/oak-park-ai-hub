# Finance Dashboard — 01 Spending Tab Redesign Spec
Daily Advancer — 2026-07-27

Companion to: Finance Dashboard - PRI 2026 (1U7n7OttHExXOmMtusu-3PuI4xBqzGz8LSiISfIMxu64)
Source context: FINANCE_DASHBOARD_MASTER_PLAN (1OsTy3PQEps-lKP_lS9IDapPOT6Rvv32NWBMezKWP6Mg)

This spec gives Codex everything needed to redesign 01 Spending into a command-center style tab
matching the visual standard of the 00 Overview tab. Read the FINANCE_DASHBOARD_MASTER_PLAN first
for overall dashboard context before implementing.

---

## Goal

The 00 Overview was rebuilt as a 2×2 KPI command-center (dark background, lime accents, card-based
layout — "ADHD-friendly finance command center"). Apply the same visual pattern to 01 Spending so
it reads as one coherent system.

Current problem with 01 Spending: it is a data table, not a command page. Opening it shows rows
of raw Tiller transactions without a clear "what happened this month" summary at the top.

Target: when Priscila opens 01 Spending, she reads the 4 most important spending facts in 3 seconds.
The detail table stays below for drill-down.

---

## Layout spec (mirrors 00 Overview design)

### App frame: rows 1–10, columns B:H

Follow the same 2×2 KPI card geometry that passed audit on 00 Overview:
- KPI card 1: B4:D6 (top-left)
- KPI card 2: F4:H6 (top-right)
- KPI card 3: B8:D10 (bottom-left)
- KPI card 4: F8:H10 (bottom-right)

Dark background: #1b1a13 fill on B1:H10 (matches 00 Overview app frame color).
Card backgrounds: #0A0A0A fill inside each 3-col × 3-row card block.
Accent color: #CBCC10 (lime) for the big number in each card.
Label text: #F2ECE0 (cream) for the card title (row 4/8), #7A7267 (muted) for unit/subtitle (row 6/10).

### The 4 KPI cards

Card 1 (top-left): TOTAL SPEND
  Row 4: label "THIS MONTH" (JetBrains Mono, uppercase, cream, 9pt)
  Row 5: big number pulled from Tiller spend sum for current month (lime, Anton or bold, 18-20pt)
  Row 6: unit "$" prefix; delta vs last month as subtitle (green if down, red if up)
  Formula: =SUMIFS(Tiller_Amount, Tiller_Date, ">="&EOMONTH(TODAY(),-1)+1, Tiller_Date, "<="&TODAY())
  (adjust range names to match the actual Tiller sheet tab name)

Card 2 (top-right): VS NORMAL
  Row 4: label "VS NORMAL" (same style)
  Row 5: delta dollar amount, positive = over budget (red lime), negative = under (green lime)
  Row 6: "above" or "below" typical month label
  Source: same NORMAL baseline used on 00 Overview (manual input cell or named range)

Card 3 (bottom-left): TOP CATEGORY
  Row 8: label "TOP CATEGORY"
  Row 9: category name (e.g. "Restaurants") — lime, bold
  Row 10: spend amount for that category this month + % of total
  Formula: requires a helper column computing category sums; reference whichever helper tab
  already does this (02 Money In or the Tiller transaction tab).

Card 4 (bottom-right): TOP MERCHANT
  Row 8: label "TOP MERCHANT"
  Row 9: merchant name (e.g. "Uber Eats") — lime, bold
  Row 10: merchant spend amount this month
  Note: current known top merchant is Uber Eats (~$3,388 month). Confirm this stays live.

### Row 11: separator
  B11:H11 — thin lime bottom border (#CBCC10, 1px). Blank row between frame and detail table.

---

## Detail table (rows 13+, starts immediately below separator)

Keep all existing Tiller transaction rows intact — do NOT delete or reformat them.
Only additions:
- Add a frozen pane at row 12 so the app frame is always visible when scrolling.
- Optionally add a Category filter dropdown at I4 for quick category drill-down (not required for MVP).

---

## Columns to keep visible / hide

Visible (A:H): Date | Amount | Description | Category | Account | (spare) | (spare) | (spare)
Hidden: any raw Tiller columns beyond H that are intermediate calculation helpers. Only hide columns
that are purely formulas with no human-readable value. DO NOT hide any column that has a SOURCE NEEDED
label or data-entry field — those stay visible.

---

## Audit checklist before shipping

Run these checks after implementation:
1. Open 01 Spending: 4 KPI cards visible at the top without scrolling.
2. Zero formula errors (#REF!, #VALUE!, #N/A) on any visible cell in B1:H10.
3. Zero SOURCE NEEDED text in visible cells.
4. Card 1 (Total Spend) matches Tiller's current MTD sum — verify against Tiller dashboard manually.
5. Card 3 and Card 4 category/merchant names are real Tiller categories — not hardcoded text.
6. Existing detail table rows still show full transaction history below row 12.
7. 00 Overview KPI values are unchanged after the edit (no broken cross-tab references).

---

## Data gaps to flag (not blocking — note in a comment cell)

The following data is MISSING from Tiller as of last audit (2026-06-24):
- Chase credit card account (not connected)
- BoA credit card account (not connected)
- Affirm (not connected)
- Cash and Investments (manual entry cells — fill if available)

If any KPI card shows $0 or #N/A due to a missing account, replace the formula result with a
yellow-flagged cell showing "INCOMPLETE — Chase/BoA/Affirm not in Tiller" so Priscila knows
the number is partial, not zero.

---

## What NOT to do

- Do not change the 00 Overview tab — it passed audit; leave it alone.
- Do not create a new catalog or move Tiller rows to a different sheet.
- Do not hardcode the spend amount — all KPI values must be live formulas.
- Do not add a chart unless all 4 KPI cards are working first.
- Do not apply this spec to 02 Money In or 03 Cards — those are separate redesigns, not included here.
