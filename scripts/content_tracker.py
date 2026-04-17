"""
content_tracker.py
==================
Shared utility — appends one row to '📊 Content Creation Log' tab every time
a pipeline runs. Import and call log_run() at the end of any script.

Tab columns (A–M):
  A  DATE         YYYY-MM-DD
  B  TIME_ET      HH:MM ET
  C  PIPELINE     capture_pipeline | capture_queue | content_creator |
                  inspiration_scraper | photo_catalog | 4am_agent
  D  TRIGGER      manual | scheduled | queue | 4am | webhook
  E  URL          source URL (or empty)
  F  NICHE        Brazil | OPC | UGC | News | Stocks | (empty)
  G  PROJECT      content | sovereign | book | (empty)
  H  STATUS       success | failed | pending | skipped | queued
  I  SCORE        1-5 (empty if not applicable)
  J  DRIVE_PATH   folder or doc URL where content landed
  K  BRIEF_URL    content brief / Google Doc URL
  L  GH_RUN_URL   GitHub Actions run URL (auto-detected from GITHUB_SERVER_URL + GITHUB_RUN_ID)
  M  NOTES        error message, extra info, etc.

Usage:
    from content_tracker import log_run

    log_run(
        pipeline="capture_pipeline",
        trigger="manual",
        url="https://www.instagram.com/reel/...",
        niche="Brazil",
        project="sovereign",
        status="success",
        score=4,
        drive_path="https://drive.google.com/...",
        brief_url="https://docs.google.com/...",
        notes="",
    )

All fields except pipeline + status are optional — pass what you have.
Non-fatal: if Sheets API fails, prints a warning and continues. Never crashes the caller.
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime
import pytz

SHEET_ID  = "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU"
TAB_NAME  = "📊 Content Creation Log"
ET        = pytz.timezone("America/New_York")


def _access_token() -> str:
    raw = os.getenv("SHEETS_TOKEN", "")
    if not raw:
        return ""
    try:
        td = json.loads(raw)
        data = urllib.parse.urlencode({
            "client_id":     td["client_id"],
            "client_secret": td["client_secret"],
            "refresh_token": td["refresh_token"],
            "grant_type":    "refresh_token",
        }).encode()
        resp = json.loads(urllib.request.urlopen(
            urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
        ).read())
        return resp.get("access_token", "")
    except Exception:
        return ""


def _gh_run_url() -> str:
    server = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    repo   = os.getenv("GITHUB_REPOSITORY", "")
    run_id = os.getenv("GITHUB_RUN_ID", "")
    if repo and run_id:
        return f"{server}/{repo}/actions/runs/{run_id}"
    return ""


def log_run(
    pipeline: str,
    status: str,
    trigger: str = "scheduled",
    url: str = "",
    niche: str = "",
    project: str = "",
    score: int | None = None,
    drive_path: str = "",
    brief_url: str = "",
    notes: str = "",
) -> bool:
    """
    Append one row to Content Creation Log.
    Returns True on success, False on failure (non-fatal either way).
    """
    token = _access_token()
    if not token:
        print("[content_tracker] SKIP — no SHEETS_TOKEN")
        return False

    now_et = datetime.now(ET)
    row = [
        now_et.strftime("%Y-%m-%d"),          # A DATE
        now_et.strftime("%H:%M"),              # B TIME_ET
        pipeline,                              # C PIPELINE
        trigger,                               # D TRIGGER
        url[:200] if url else "",              # E URL
        niche,                                 # F NICHE
        project,                               # G PROJECT
        status,                                # H STATUS
        score if score is not None else "",    # I SCORE
        drive_path[:300] if drive_path else "", # J DRIVE_PATH
        brief_url[:300] if brief_url else "",   # K BRIEF_URL
        _gh_run_url(),                          # L GH_RUN_URL
        notes[:500] if notes else "",           # M NOTES
    ]

    enc = urllib.parse.quote(f"'{TAB_NAME}'!A:M", safe="!:'")
    api_url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}"
        f"/values/{enc}:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS"
    )
    body = json.dumps({"values": [row]}).encode()
    try:
        urllib.request.urlopen(
            urllib.request.Request(
                api_url, data=body,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            )
        ).read()
        print(f"[content_tracker] ✓ logged — {pipeline} / {status}")
        return True
    except Exception as e:
        print(f"[content_tracker] WARNING — could not log: {e}")
        return False
