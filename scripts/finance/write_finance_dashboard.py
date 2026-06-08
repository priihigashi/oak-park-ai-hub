"""
One-shot: writes NPER debt payoff formulas to the Finance Dashboard spreadsheet.
Spreadsheet: 1U7n7OttHExXOmMtusu-3PuI4xBqzGz8LSiISfIMxu64
Tabs touched: 01 Cards Master, 02 Debt Payoff Simulator, 03 Decisions Log
Run: python write_finance_dashboard.py (needs SHEETS_TOKEN + PRI_OP_GMAIL_APP_PASSWORD env vars)
"""
import os
import json
import smtplib
import urllib.request
import urllib.parse
from email.mime.text import MIMEText

import gspread
from google.oauth2.credentials import Credentials


def get_creds():
    td = json.loads(os.environ["SHEETS_TOKEN"])
    data = urllib.parse.urlencode({
        "client_id":     td["client_id"],
        "client_secret": td["client_secret"],
        "refresh_token": td["refresh_token"],
        "grant_type":    "refresh_token",
    }).encode()
    resp = json.loads(urllib.request.urlopen(
        "https://oauth2.googleapis.com/token", data=data
    ).read())
    return Credentials(
        token=resp["access_token"],
        refresh_token=td["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=td["client_id"],
        client_secret=td["client_secret"],
    )


def write_cards_master(sh):
    ws = sh.worksheet("01 Cards Master")
    ws.update(
        "A2:B6",
        [
            ["Discover",        "Discover"],
            ["Chase",           "Chase"],
            ["Bank of America", "Bank of America"],
            ["Citi",            "Citi"],
            ["Affirm",          "Affirm"],
        ],
        value_input_option="USER_ENTERED",
    )
    print("OK 01 Cards Master -- card names written (A2:B6)")


def write_simulator(sh):
    ws = sh.worksheet("02 Debt Payoff Simulator")

    # Helper to build one card row (5 cards, referencing rows 2-6 of Cards Master)
    def card_row(r):
        cm_row = r - 3  # row 5 -> cm row 2, row 6 -> cm row 3, etc.
        return [
            f"='01 Cards Master'!A{cm_row}",
            f"='01 Cards Master'!C{cm_row}",
            f"='01 Cards Master'!D{cm_row}",
            f"='01 Cards Master'!E{cm_row}",
            f'=IFERROR(CEILING(NPER(C{r}/100/12,-D{r},B{r}),1),"")',
            f'=IFERROR(ROUND(E{r}*D{r}-B{r},2),"")',
            f'=IFERROR(CEILING(NPER(C{r}/100/12,-(D{r}+100),B{r}),1),"")',
            f'=IFERROR(ROUND(G{r}*(D{r}+100)-B{r},2),"")',
            f'=IFERROR(CEILING(NPER(C{r}/100/12,-(D{r}+200),B{r}),1),"")',
            f'=IFERROR(ROUND(I{r}*(I{r}+200)-B{r},2),"")',
            f'=IFERROR(ROUND(F{r}-J{r},2),"")',
            f'=IFERROR(RANK(B{r},$B$5:$B$9,1),"")',
            f'=IFERROR(RANK(C{r},$C$5:$C$9,0),"")',
        ]

    E = ["", "", "", "", "", "", "", "", "", "", "", "", ""]  # empty row

    data = [
        # Row 1
        ["DEBT PAYOFF SIMULATOR -- Auto-updates when 01 Cards Master is filled"] + [""] * 12,
        # Row 2
        ["NOTE: Months assumes stated minimum as a FIXED payment. Snowball = lowest balance first. Avalanche = highest APR first."] + [""] * 12,
        # Row 3
        E,
        # Row 4 headers
        [
            "Card", "Balance ($)", "APR (%)", "Min Pmt ($)",
            "Min Only -- Months", "Min Only -- Interest ($)",
            "+$100/mo -- Months", "+$100/mo -- Interest ($)",
            "+$200/mo -- Months", "+$200/mo -- Interest ($)",
            "Interest Saved (+$200)", "Snowball Order", "Avalanche Order",
        ],
        card_row(5),   # Discover
        card_row(6),   # Chase
        card_row(7),   # Bank of America
        card_row(8),   # Citi
        card_row(9),   # Affirm
        E,
        # Row 11 TOTALS
        ["TOTALS", "=SUM(B5:B9)", "", "", "", "=SUM(F5:F9)", "", "=SUM(H5:H9)", "", "=SUM(J5:J9)", "=SUM(K5:K9)", "", ""],
        E,
        # Row 13 PAYOFF SUMMARY
        ["PAYOFF SUMMARY", "Min Only", "+$100/mo", "+$200/mo"] + [""] * 9,
        # Row 14
        ['=IFERROR(MAX(E5:E9),"")', '=IFERROR(MAX(G5:G9),"")', '=IFERROR(MAX(I5:I9),"")', "", "Months to clear all debt"] + [""] * 8,
        # Row 15
        ['=IFERROR(SUM(F5:F9),"")', '=IFERROR(SUM(H5:H9),"")', '=IFERROR(SUM(J5:J9),"")', "", "Total interest paid ($)"] + [""] * 8,
        E,
        # Row 17 Snowball tip
        ["SNOWBALL: Pay minimums on all cards, then put every extra dollar toward the LOWEST BALANCE first. Fast wins build momentum."] + [""] * 12,
        # Row 18 Avalanche tip
        ["AVALANCHE: Pay minimums on all cards, then put every extra dollar toward the HIGHEST APR first. Mathematically optimal -- saves the most interest."] + [""] * 12,
    ]

    ws.update("A1:M18", data, value_input_option="USER_ENTERED")
    print("OK 02 Debt Payoff Simulator -- NPER formulas written (A1:M18)")


def write_decisions_log(sh):
    ws = sh.worksheet("03 Decisions Log")
    data = [
        ["DECISIONS LOG -- Track every financial decision with context and revisit dates"] + [""] * 5,
        [""] * 6,
        ["Date", "Decision", "Context / Options", "Revisit Date", "Status", "Notes"],
        [
            "2026-06-08",
            "Payoff order: Snowball vs Avalanche?",
            "Use 02 Debt Payoff Simulator after filling 01 Cards Master. Snowball = fastest psychological win. Avalanche = least total interest.",
            "2026-06-15", "PENDING",
            "Decide after adding real balances + APRs",
        ],
        [
            "2026-06-08",
            "Discover card: Keep open or close?",
            "Closing oldest card reduces avg account age and can hurt credit score. Benefit: simplicity. Risk: score drop.",
            "2026-06-22", "PENDING",
            "Check credit report for account open date first",
        ],
        [
            "2026-06-08",
            "Affirm: Priority level for payoff?",
            "Check Affirm app for actual APR (some plans 0% promo, others 36%). Priority depends on rate.",
            "2026-06-15", "PENDING",
            "Open Affirm app to confirm rate before ranking",
        ],
        [
            "2026-06-08",
            "Phase 2: App vs sheet long-term?",
            "Phase 1 = Google Sheets (this week). Phase 2 = Vercel app conversion for mobile-friendly view. Evaluate at end of week.",
            "2026-06-12", "PENDING",
            "Revisit at end-of-week scoping session",
        ],
    ]
    ws.update("A1:F7", data, value_input_option="USER_ENTERED")
    print("OK 03 Decisions Log -- headers + 4 decisions written (A1:F7)")


def send_summary_email():
    pw = os.environ.get("PRI_OP_GMAIL_APP_PASSWORD", "")
    if not pw:
        print("SKIP email -- PRI_OP_GMAIL_APP_PASSWORD not set")
        return

    body = """\
Finance Dashboard formulas are live!

Open your spreadsheet:
https://docs.google.com/spreadsheets/d/1U7n7OttHExXOmMtusu-3PuI4xBqzGz8LSiISfIMxu64

Written today (2026-06-08):
* 01 Cards Master -- Discover, Chase, Bank of America, Citi, Affirm in A2:B6
* 02 Debt Payoff Simulator -- NPER formula grid (A1:M18)
  - Min-only, +$100/mo, +$200/mo payoff scenarios
  - Snowball order (lowest balance first) + Avalanche order (highest APR first)
  - Summary section: months to clear all debt + total interest by scenario
* 03 Decisions Log -- 4 pre-loaded pending decisions (A1:F7)

YOUR NEXT STEP (before Friday June 12):
Open 01 Cards Master and fill in real numbers from your card apps/statements:
  Col C: Balance ($)
  Col D: APR (%)
  Col E: Min Payment ($)
  Col F: Due Date
  Col G: Statement Date
  Col H: Credit Limit

The Simulator updates automatically once you fill those in.
"""
    msg = MIMEText(body)
    msg["Subject"] = "Finance Dashboard formulas are LIVE -- fill in your card numbers"
    msg["From"] = "Oak Park AI <priscila@oakpark-construction.com>"
    msg["To"] = "priscila@oakpark-construction.com"

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login("priscila@oakpark-construction.com", pw)
        s.send_message(msg)
    print("OK Summary email sent to priscila@oakpark-construction.com")


if __name__ == "__main__":
    gc = gspread.authorize(get_creds())
    sh = gc.open_by_key("1U7n7OttHExXOmMtusu-3PuI4xBqzGz8LSiISfIMxu64")

    write_cards_master(sh)
    write_simulator(sh)
    write_decisions_log(sh)
    send_summary_email()

    print("DONE Finance Dashboard setup complete.")
