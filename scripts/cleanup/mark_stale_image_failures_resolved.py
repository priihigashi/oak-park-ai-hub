#!/usr/bin/env python3
"""Bulk-resolve stale image-provider failures in the Pipeline Failures tab.

After IMAGE_FALLBACK_SKIP landed in PR #197, the upstream causes that produced
these rows no longer fire on new runs. Mark them resolved so the unresolved
backlog reflects only actionable failures.

Targets (only when the row is unresolved):
  - replicate/* HTTP Error 429 (Seedream 5.0 Lite, SDXL, Seedream 4.5 — all rate-limited burst dispatch)
  - nb2/gemini-3.1-flash HTTP Error 402 OR 403 (provider on IMAGE_FALLBACK_SKIP)
  - pexels/* HTTP Error 403 (rate limited, cascade falls through to Wikimedia)
  - pixabay/* HTTP Error 429/403 (same cascade behavior)

Run from CI or locally. Idempotent.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SHEET_ID = os.environ.get("CONTENT_SHEET_ID", "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU")
TAB = "🚨 Pipeline Failures"
RESOLUTION = "yes (image cascade backed-off post PR #197; provider rate/credit gates now active)"


_TARGET_PATTERNS = [
    re.compile(r"replicate/.*HTTP Error 429", re.IGNORECASE),
    re.compile(r"replicate/.*Too Many Requests", re.IGNORECASE),
    re.compile(r"nb2/gemini.*HTTP Error 40[23]", re.IGNORECASE),
    re.compile(r"pexels/.*HTTP Error 40[3]", re.IGNORECASE),
    re.compile(r"pixabay/.*HTTP Error 40[23]", re.IGNORECASE),
    re.compile(r"pixabay/.*HTTP Error 429", re.IGNORECASE),
]


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


def _matches(row_text: str) -> bool:
    return any(p.search(row_text) for p in _TARGET_PATTERNS)


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
        raise SystemExit("No RESOLVED column in Pipeline Failures tab.")

    updates = []
    by_pattern = {}
    for row_num, row in enumerate(rows[1:], start=2):
        already = row[resolved_idx].strip() if resolved_idx < len(row) else ""
        if already:
            continue
        stage = row[3] if len(row) > 3 else ""
        error = row[4] if len(row) > 4 else ""
        combined = f"{stage} {error}"
        if _matches(combined):
            updates.append({
                "range": f"'{TAB}'!{_col_letter(resolved_idx + 1)}{row_num}",
                "values": [[RESOLUTION]],
            })
            key = stage.split("/")[0] if "/" in stage else stage
            by_pattern[key] = by_pattern.get(key, 0) + 1

    if not updates:
        print("No stale image-provider rows matched.")
        return

    # Chunk to avoid Sheets API payload limits (1000 ranges per batchUpdate).
    CHUNK = 500
    total = 0
    for i in range(0, len(updates), CHUNK):
        chunk = updates[i:i + CHUNK]
        svc.spreadsheets().values().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={"valueInputOption": "USER_ENTERED", "data": chunk},
        ).execute()
        total += len(chunk)
        print(f"  batch {i//CHUNK + 1}: {len(chunk)} rows marked resolved")
    print(f"\nTotal: {total} row(s) marked resolved.")
    print("By provider:")
    for k, v in sorted(by_pattern.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
