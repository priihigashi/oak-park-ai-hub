#!/usr/bin/env python3
"""Mark known image-provider 402 failures as resolved in the Pipeline Failures tab."""

from __future__ import annotations

import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SHEET_ID = os.environ.get("CONTENT_SHEET_ID", "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU")
TAB = "🚨 Pipeline Failures"
RESOLUTION = "yes (provider disabled 2026-06-08)"


def _credentials() -> Credentials:
    raw = os.environ.get("SHEETS_TOKEN", "")
    if raw:
        creds = Credentials.from_authorized_user_info(json.loads(raw))
    else:
        token_path = Path.home() / "ClaudeWorkspace" / "Credentials" / "sheets_token.json"
        creds = Credentials.from_authorized_user_file(str(token_path))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def _col_letter(idx: int) -> str:
    out = ""
    while idx:
        idx, rem = divmod(idx - 1, 26)
        out = chr(65 + rem) + out
    return out


def main() -> None:
    svc = build("sheets", "v4", credentials=_credentials())
    rows = svc.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{TAB}'",
    ).execute().get("values", [])
    if not rows:
        print("No Pipeline Failures rows found.")
        return

    header = rows[0]
    hmap = {h.strip().lower(): i for i, h in enumerate(header)}
    resolved_idx = hmap.get("resolved")
    if resolved_idx is None:
        resolved_idx = len(header)
        header.append("RESOLVED")
        svc.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=f"'{TAB}'!A1:{_col_letter(len(header))}1",
            valueInputOption="USER_ENTERED",
            body={"values": [header]},
        ).execute()

    updates = []
    for row_num, row in enumerate(rows[1:], start=2):
        haystack = " ".join(str(c) for c in row).lower()
        already = row[resolved_idx].strip().lower() if resolved_idx < len(row) else ""
        if already:
            continue
        if "http error 402" in haystack or "payment required" in haystack:
            updates.append({
                "range": f"'{TAB}'!{_col_letter(resolved_idx + 1)}{row_num}",
                "values": [[RESOLUTION]],
            })

    if not updates:
        print("No unresolved HTTP 402 rows found.")
        return
    svc.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"valueInputOption": "USER_ENTERED", "data": updates},
    ).execute()
    print(f"Marked {len(updates)} HTTP 402 row(s) resolved.")


if __name__ == "__main__":
    main()
