#!/usr/bin/env python3
"""Append one row to the '🚨 Pipeline Failures' tab when a workflow job fails.

WHY THIS EXISTS (found 2026-08-05)
----------------------------------
The rule in CLAUDE.md is: "every workflow that catches an exception MUST call
log_pipeline_failure". content_creator.yml did not. Its only failure handling
was an alert email, so when the job went red the 🚨 Pipeline Failures tab stayed
silent.

The consequence was a **false all-clear**. The tab's last row is dated
2026-04-29. content_creator.yml then failed five consecutive scheduled runs —
2026-06-13, 06-16, 06-19, 06-22, 06-25 — and not one of them appears in the tab.
Meanwhile session-start's documented check is "scan the tab for unresolved rows",
which kept reporting clean while the content pipeline was dead. The crons were
paused on 2026-06-26 off the back of those red runs, and the tab never knew.

DESIGN
------
Deliberately dependency-free (stdlib urllib only) and best-effort: this runs in
an `if: failure()` step and must never itself fail the job or mask the real
error. It mints a fresh access token via a refresh_token grant — it does NOT
reuse the access token baked into SHEETS_TOKEN, which is the stale-token bug
fixed elsewhere on 2026-08-05.

Usage (from a workflow step):
    python scripts/log_workflow_failure.py \
        --workflow "content_creator.yml" \
        --stage "create-content"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime

FAILURES_SHEET_ID = "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU"
FAILURES_TAB = "🚨 Pipeline Failures"
# Column order is fixed by the tab and must not drift:
# TIMESTAMP_UTC | WORKFLOW | RUN_ID | STAGE | ERROR | RUN_URL | RESOLVED | NOTE
EXPECTED_HEADER = ["TIMESTAMP_UTC", "WORKFLOW", "RUN_ID", "STAGE",
                   "ERROR", "RUN_URL", "RESOLVED", "NOTE"]


def _access_token() -> str:
    """Mint a fresh access token from the refresh_token in SHEETS_TOKEN."""
    raw = os.environ.get("SHEETS_TOKEN", "")
    if not raw:
        print("[log_workflow_failure] SHEETS_TOKEN not set — cannot log", file=sys.stderr)
        return ""
    td = json.loads(raw)
    for key in ("client_id", "client_secret", "refresh_token"):
        if not td.get(key):
            print(f"[log_workflow_failure] SHEETS_TOKEN missing {key} — cannot log",
                  file=sys.stderr)
            return ""
    body = urllib.parse.urlencode({
        "client_id": td["client_id"],
        "client_secret": td["client_secret"],
        "refresh_token": td["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=body)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())["access_token"]


def append_failure(workflow: str, stage: str, error: str, note: str = "") -> bool:
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "priihigashi/oak-park-ai-hub")
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}" if run_id else ""
    row = [
        datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        workflow,
        run_id or "—",
        stage,
        (error or "job failed — see run log")[:500],
        run_url,
        "",       # RESOLVED — intentionally blank; that is what makes it show up
        note[:300],
    ]
    token = _access_token()
    if not token:
        return False
    tab = urllib.parse.quote(FAILURES_TAB, safe="")
    url = (f"https://sheets.googleapis.com/v4/spreadsheets/{FAILURES_SHEET_ID}"
           f"/values/{tab}!A:H:append"
           f"?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS")
    req = urllib.request.Request(
        url, data=json.dumps({"values": [row]}).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        resp = json.loads(r.read())
    # KRM #18: confirm which tab actually received the write, never assume.
    updated = (resp.get("updates") or {}).get("updatedRange", "")
    print(f"[log_workflow_failure] appended to {updated or '(range not reported)'}")
    if updated and FAILURES_TAB not in updated:
        print(f"[log_workflow_failure] WARNING: row landed in {updated}, "
              f"not '{FAILURES_TAB}'", file=sys.stderr)
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--error", default="")
    ap.add_argument("--note", default="")
    args = ap.parse_args()
    try:
        append_failure(args.workflow, args.stage, args.error, args.note)
    except Exception as exc:  # best-effort: never mask the real job failure
        print(f"[log_workflow_failure] non-fatal: {exc}", file=sys.stderr)
    return 0  # always 0 — the job is already failing for its own reason


if __name__ == "__main__":
    raise SystemExit(main())
