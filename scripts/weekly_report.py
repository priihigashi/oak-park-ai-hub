#!/usr/bin/env python3
"""
weekly_report.py
================
Weekly content pipeline summary email.
Runs every Monday 9AM ET via weekly-report.yml.

Reads the live Ideas & Inbox workbook configured by CONTENT_SHEET_ID:
  - 📋 Content Queue
  - 🚨 Pipeline Failures
  - 📥 Inspiration Library

Saves HTML report to WEEKLY_REPORTS_FOLDER_ID in Drive.
Emails to NOTIFY_EMAIL via SMTP (PRI_OP_GMAIL_APP_PASSWORD).
"""

import json
import os
import smtplib
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CONTENT_SHEET_ID      = os.getenv("CONTENT_SHEET_ID", "")
IDEAS_SHEET_ID        = "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU"
WEEKLY_REPORTS_FOLDER = os.getenv("WEEKLY_REPORTS_FOLDER_ID", "1gETNHiEtbkjYRimJOccDR9zssWSM4vNM")
NOTIFY_EMAIL          = os.getenv("NOTIFY_EMAIL", "priscila@oakpark-construction.com")
FROM_EMAIL            = "priscila@oakpark-construction.com"

CONTENT_QUEUE_TAB      = "📋 Content Queue"
PIPELINE_FAILURES_TAB  = "🚨 Pipeline Failures"
INSPIRATION_LIB_TAB    = "📥 Inspiration Library"


def _access_token() -> str:
    raw = os.getenv("SHEETS_TOKEN", "")
    if not raw:
        raise RuntimeError("SHEETS_TOKEN env var not set")
    td = json.loads(raw)
    body = urllib.parse.urlencode({
        "client_id": td["client_id"],
        "client_secret": td["client_secret"],
        "refresh_token": td["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    resp = json.loads(urllib.request.urlopen(
        urllib.request.Request("https://oauth2.googleapis.com/token", body)
    ).read())
    return resp["access_token"]


def _sheet_values(token: str, sheet_id: str, tab: str) -> list:
    enc = urllib.parse.quote(f"'{tab}'!A:Z", safe="!:'")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{enc}"
    try:
        resp = urllib.request.urlopen(
            urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        ).read()
        return json.loads(resp).get("values", [])
    except Exception as exc:
        raise RuntimeError(f"could not read {tab}: {exc}") from exc


def _col(header_row: list, name: str) -> int:
    for i, h in enumerate(header_row):
        if name.lower() in str(h).lower():
            return i
    return -1


def _content_stats(rows: list) -> dict:
    if len(rows) < 2:
        return {"by_status": {}, "new_this_week": 0}
    headers = rows[0]
    status_col = _col(headers, "status")
    date_col = _col(headers, "date")
    if status_col < 0:
        raise RuntimeError("📋 Content Queue has no Status column")
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    totals: dict = {}
    new_this_week = 0
    for row in rows[1:]:
        status = row[status_col].strip() if len(row) > status_col else ""
        if not status:
            continue
        totals[status] = totals.get(status, 0) + 1
        if date_col >= 0 and len(row) > date_col:
            try:
                d = datetime.fromisoformat(row[date_col].replace("Z", "+00:00"))
                if d.tzinfo is None:
                    d = d.replace(tzinfo=timezone.utc)
                if d >= week_ago:
                    new_this_week += 1
            except Exception:
                pass
    return {"by_status": totals, "new_this_week": new_this_week}


def _pipeline_failures(rows: list) -> list:
    if len(rows) < 2:
        return []
    headers = rows[0]
    resolved_col = _col(headers, "resolved")
    stage_col = _col(headers, "stage")
    error_col = _col(headers, "error")
    date_col = _col(headers, "date")
    unresolved = []
    for row in rows[1:]:
        if resolved_col >= 0 and len(row) > resolved_col and row[resolved_col].strip():
            continue
        stage = row[stage_col] if stage_col >= 0 and len(row) > stage_col else "?"
        error = row[error_col] if error_col >= 0 and len(row) > error_col else "?"
        date = row[date_col] if date_col >= 0 and len(row) > date_col else "?"
        unresolved.append({"stage": stage, "error": error[:120], "date": date})
    return unresolved


def _inspiration_blank_count(rows: list) -> int:
    if len(rows) < 2:
        return 0
    blank = 0
    for row in rows[1:]:
        if len(row) < 7 or not row[6].strip():
            if row and any(c.strip() for c in row):
                blank += 1
    return blank


def _build_html(stats: dict, failures: list, blank_g: int, week_str: str) -> str:
    by_status = stats.get("by_status", {})
    new_week = stats.get("new_this_week", 0)
    status_rows = ""
    for status, count in sorted(by_status.items(), key=lambda x: -x[1]):
        color = "#d4edda" if "posted" in status.lower() else \
                "#fff3cd" if "approved" in status.lower() else \
                "#f8d7da" if "hold" in status.lower() or "fail" in status.lower() else "#fff"
        status_rows += (
            f'<tr style="background:{color}">'
            f'<td style="padding:6px 12px">{status}</td>'
            f'<td style="padding:6px 12px;text-align:right"><b>{count}</b></td>'
            f'</tr>'
        )
    fail_rows = ""
    for f in failures[:10]:
        fail_rows += (
            f'<tr>'
            f'<td style="padding:6px 12px;font-size:11px">{f["date"]}</td>'
            f'<td style="padding:6px 12px">{f["stage"]}</td>'
            f'<td style="padding:6px 12px;font-size:11px;color:#c00">{f["error"]}</td>'
            f'</tr>'
        )
    if not fail_rows:
        fail_rows = (
            '<tr><td colspan="3" style="padding:10px;color:green;text-align:center">'
            '&#x2705; No unresolved pipeline failures'
            '</td></tr>'
        )
    return f"""
<html><body style="font-family:Arial,sans-serif;color:#333;max-width:700px;margin:0 auto">
<h2 style="color:#1c1409">&#x1F4CA; Weekly Pipeline Report &#x2014; {week_str}</h2>
<h3>Content Pipeline</h3>
<p>New queue items this week: <b>{new_week}</b> | Inspiration Library backlog (blank G): <b>{blank_g}</b></p>
<table style="border-collapse:collapse;width:100%">
  <thead style="background:#1c1409;color:#f0e8d6"><tr><th style="padding:8px;text-align:left">Status</th><th style="padding:8px;text-align:right">Count</th></tr></thead>
  <tbody>{status_rows}</tbody>
</table>
<h3 style="margin-top:24px">Pipeline Failures (unresolved)</h3>
<table style="border-collapse:collapse;width:100%">
  <thead style="background:#c00;color:#fff"><tr><th style="padding:8px;text-align:left">Date</th><th style="padding:8px;text-align:left">Stage</th><th style="padding:8px;text-align:left">Error</th></tr></thead>
  <tbody>{fail_rows}</tbody>
</table>
<p style="margin-top:24px;font-size:12px;color:#888">
  <a href="https://docs.google.com/spreadsheets/d/1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU">Ideas &amp; Inbox</a> · Generated by weekly-report.yml
</p>
</body></html>
"""


def _save_to_drive(token: str, html_content: str, filename: str):
    meta = json.dumps({"name": filename, "parents": [WEEKLY_REPORTS_FOLDER]}).encode()
    content = html_content.encode()
    boundary = "weekly-report-boundary"
    b = boundary.encode()
    body = (
        b"--" + b + b"\r\n"
        b"Content-Type: application/json; charset=UTF-8\r\n\r\n"
        + meta + b"\r\n"
        b"--" + b + b"\r\n"
        b"Content-Type: text/html\r\n\r\n"
        + content + b"\r\n"
        b"--" + b + b"--\r\n"
    )
    req = urllib.request.Request(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/related; boundary={boundary}",
        },
    )
    try:
        resp = json.loads(urllib.request.urlopen(req).read())
        fid = resp.get("id", "")
        if not fid:
            raise RuntimeError(f"Drive upload returned no file id: {resp}")
        print(f"Saved report to Drive: {fid}")
        return f"https://drive.google.com/file/d/{fid}/view"
    except Exception as exc:
        raise RuntimeError(f"Drive upload failed: {exc}") from exc


def _send_email(subject: str, html_body: str) -> None:
    pwd = os.getenv("PRI_OP_GMAIL_APP_PASSWORD", "")
    if not pwd:
        raise RuntimeError("PRI_OP_GMAIL_APP_PASSWORD not set — email not sent")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = NOTIFY_EMAIL
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(FROM_EMAIL, pwd)
        s.send_message(msg)
    print(f"Email sent to {NOTIFY_EMAIL}")


def main() -> None:
    if not CONTENT_SHEET_ID:
        raise RuntimeError("CONTENT_SHEET_ID env var not set")
    token = _access_token()
    week_str = datetime.now(timezone.utc).strftime("Week of %Y-%m-%d")
    cq_rows = _sheet_values(token, CONTENT_SHEET_ID, CONTENT_QUEUE_TAB)
    pf_rows = _sheet_values(token, IDEAS_SHEET_ID, PIPELINE_FAILURES_TAB)
    lib_rows = _sheet_values(token, IDEAS_SHEET_ID, INSPIRATION_LIB_TAB)
    stats = _content_stats(cq_rows)
    failures = _pipeline_failures(pf_rows)
    blank_g = _inspiration_blank_count(lib_rows)
    html = _build_html(stats, failures, blank_g, week_str)
    filename = f"Weekly_Report_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.html"
    drive_url = _save_to_drive(token, html, filename)
    print(f"Report saved: {drive_url}")
    _send_email(f"📊 Weekly Pipeline Report — {week_str}", html)
    if failures:
        print(f"WARN: {len(failures)} unresolved pipeline failure(s)")


if __name__ == "__main__":
    main()
