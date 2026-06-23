# Finance Dashboard — Merchant Alias + Needs Detail Codex Brief
# Compiled: 2026-06-23 from Finance Dashboard punch list
# Source doc: https://docs.google.com/document/d/1OsTy3PQEps-lKP_lS9IDapPOT6Rvv32NWBMezKWP6Mg
# Dashboard: https://docs.google.com/spreadsheets/d/1U7n7OttHExXOmMtusu-3PuI4xBqzGz8LSiISfIMxu64

## CONTEXT

Phase 1 build is source-ready (verified 2026-06-23, 0 formula errors, baseline $3,213.73).
The Spending tab works correctly but shows payment rails (PayPal, Zelle) instead of stores,
and fixed bills crowd out discretionary insight. This brief specifies the cleanup.

---

## STEP 0 — BACKUP FIRST (non-negotiable)

Before any edit: make a backup copy of the Finance Dashboard named:
"BACKUP — Finance Dashboard PRI 2026 — [today's date]"
Store in Personal Finance folder (Drive ID: 11v1azo25sq8TdT-rAP1eltpZuIFphov8).
Verify backup exists before proceeding.

---

## TASK 1 — Merchant alias rules in _FACT_TXN

Expand the existing merchant alias/normalization logic in the _FACT_TXN hidden tab.
Apply these rules IN ORDER (first match wins):

### PayPal pass-through aliases (PayPal is the rail, not the store)
PAYPAL *UBER*          -> UBER EATS
PAYPAL *MCDONALDS*     -> MCDONALD'S
PAYPAL *SHEINUSSERV*   -> SHEIN
PAYPAL *NETFLIX*       -> NETFLIX
PAYPAL *APPLE*         -> APPLE
PAYPAL *MICROSOFT*     -> MICROSOFT
PAYPAL *CANVA*         -> CANVA
PAYPAL *SLING*         -> SLING TV
PAYPAL *HOME DEPOT*    -> HOME DEPOT
PAYPAL *PRIME*         -> AMAZON PRIME
PAYPAL *AMAZON*        -> AMAZON

### Opaque PayPal rows — do NOT fake a merchant name
PAYPAL DEBIT OID*      -> NEEDS DETAIL
PAYPAL DEBIT*          -> NEEDS DETAIL (if no further identifier)
PAYPAL *PMNT*          -> NEEDS DETAIL

### Amazon normalization
AMAZON PRIME*          -> AMAZON PRIME
AMAZON.COM*            -> AMAZON
AMZN*                  -> AMAZON

### Big-box normalization
TARGET T-*             -> TARGET
WM SUPERCENTER*        -> WALMART
WALMART*               -> WALMART
WHOLEFDS*              -> WHOLE FOODS

### Person payments (Zelle / Venmo) — keep as-is but label as PERSONAL TRANSFER
ZELLE PAYMENT TO*      -> extract recipient name + label category as PERSONAL TRANSFER
ZELLE*                 -> PERSONAL TRANSFER if no clear merchant name

### Fixed-cost categories (keep visible but secondary in the main view)
RV SCHOOLS*            -> RV SCHOOLS (Tuition) [category: FIXED - EDUCATION]
Any row categorized as loan repayment -> FIXED - LOAN

---

## TASK 2 — Needs Detail table on 01 Spending

Add a "Needs Detail" section to the 01 Spending tab (below the main spend table, not above).

Schema (one row per opaque transaction):
  Date | Description (raw) | Normalized to | Amount | Account | Category | Suggested Action

Rows to include:
- Any transaction where normalized merchant = "NEEDS DETAIL"
- Any row with blank Category
- Any CHECKCARD / PURCHASE / PMNT SENT rows in the current period that have no clear merchant

Current known rows to surface (as of 2026-06-23 audit):
- 2026-06-08  PAYPAL DEBIT OID 39980279  $87.69   Chase  Shopping
- 2026-06-08  PAYPAL DEBIT OID 39967815  $504.99  Chase  Shopping
- 2026-05-22  PAYPAL DEBIT OID 39757453  $154.99  Chase  Shopping

Suggested Action column options:
- "Check PayPal history for OID [number]"
- "Categorize manually"
- "Confirm transfer vs purchase"

---

## TASK 3 — Variable Spend view on 01 Spending

The primary merchant table must answer "where did my money go?" — not "what did I pay through."

Redesign the 01 Spending primary table to show VARIABLE / ACTIONABLE spend:
- Variable spend = everything EXCEPT fixed bills (tuition, loan repayment, subscriptions with
  fixed monthly amounts like Netflix, Sling, Canva, Amazon Prime).
- Fixed bills move to a secondary section labeled "Fixed Monthly" — still visible but below.
- Primary table headline: "Variable Spending This Month" with % of total spend.

Do NOT exclude opaque PayPal from MTD totals — unknown spend counts, it just gets surfaced
in the Needs Detail table for classification.

---

## TASK 4 — Chart and label clarity

- Any chart currently titled "All Spend" or "Spending by Category": rename to include scope.
  Suggested: "All Spend by Category — MTD" vs "Variable Spend by Merchant — MTD".
- Overview tab Personal Cashflow copy: soften the framing so it reads as a household
  snapshot, not a complete business/household reality statement.

---

## TASK 5 — Verification criteria (run after ALL tasks)

1. 0 formula errors in the entire workbook (use the error-count pattern from previous sessions).
2. MTD personal spend total is UNCHANGED from pre-edit baseline ($3,213.73) unless a
   specific classification change intentionally moves a row.
3. VS NORMAL recomputes correctly after any alias changes.
4. All charts still have series (no #REF or broken feeds).
5. PayPal Debit OID rows appear in Needs Detail table AND count in MTD totals.
6. No new double-counting: confirm PayPal is still not connected as a separate Tiller account.
7. Variable Spend view shows a plausible top-5 discretionary merchant list (not dominated by
   PayPal, Zelle, or tuition).

Report back: baseline MTD before vs MTD after, # rows in Needs Detail, # aliases applied,
0 formula errors confirmed.

---

## WHAT THIS DOES NOT INCLUDE (deferred)

- PayPal Tiller connection — waiting on Priscila to connect in Tiller UI first.
  After connection: Codex must implement _PAYPAL_DETAIL_MATCH dedupe before PayPal data
  counts in any totals. See master plan doc for full spec.
- Classifying 31 owner/Michael transfer rows ($48,872.58) — Priscila's decision only.
- Filling missing card APRs, limits, due dates — manual input by Priscila.
