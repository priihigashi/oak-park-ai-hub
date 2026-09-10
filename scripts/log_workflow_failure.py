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


def _read_range(token: str, a1: str) -> list[list[str]]:
    """GET one range. Returns [] on any failure rather than raising."""
    tab_range = urllib.parse.quote(a1, safe="")
    url = (f"https://sheets.googleapis.com/v4/spreadsheets/{FAILURES_SHEET_ID}"
           f"/values/{tab_range}")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read()).get("values", []) or []
    except Exception as exc:
        print(f"[log_workflow_failure] read {a1} failed: {exc}", file=sys.stderr)
        return []


def _header_ok(token: str) -> bool:
    """Refuse to write when the tab's columns have drifted.

    EXPECTED_HEADER was declared in the original fix but never checked, so a
    renamed or reordered column would have silently written every field into the
    wrong place -- worse than not logging, because it looks logged.
    """
    rows = _read_range(token, f"{FAILURES_TAB}!A1:H1")
    actual = [c.strip() for c in (rows[0] if rows else [])]
    if actual[:len(EXPECTED_HEADER)] == EXPECTED_HEADER:
        return True
    print(f"[log_workflow_failure] HEADER DRIFT: expected {EXPECTED_HEADER}, "
          f"found {actual} — refusing to write", file=sys.stderr)
    return False


def run_key() -> str:
    """The identity of one ATTEMPT, not one run.

    GITHUB_RUN_ID stays constant when a workflow is re-run; GitHub exposes
    GITHUB_RUN_ATTEMPT precisely because each re-run is a distinct attempt,
    counting from 1. Keying dedup on RUN_ID alone therefore throws away real
    evidence: attempt 1 fails today, you re-run tomorrow, attempt 2 fails the
    same way, and the logger says "already logged — skipping duplicate".

    Storing `<run_id>:<attempt>` in the existing RUN_ID column keeps every
    attempt distinct with no sheet migration and no new column.
    """
    rid = os.environ.get("GITHUB_RUN_ID", "")
    if not rid:
        return ""
    return f"{rid}:{os.environ.get('GITHUB_RUN_ATTEMPT', '1')}"


def _already_logged(token: str, key: str, stage: str) -> bool:
    """Idempotency: (RUN_ID:ATTEMPT, STAGE) is the natural key for one failure.

    Two `if: failure()` steps inside the SAME attempt still dedup, which is the
    duplicate this guard exists to stop. A separate re-run does not.
    """
    if not key:
        return False
    rows = _read_range(token, f"{FAILURES_TAB}!C2:D")
    return any(len(r) >= 2 and r[0].strip() == key and r[1].strip() == stage
               for r in rows)


def _readback_matches(token: str, updated: str, expected_key: str) -> bool:
    """Confirm the row is really in the tab. An append receipt is not evidence.

    Compared exactly, not by substring: `"123" in "1234:1"` is true, so a
    substring test would accept a DIFFERENT run's row as proof that this one
    landed -- a readback that can pass on the wrong row is not a readback.
    """
    if not updated:
        return False
    rows = _read_range(token, updated)
    return any((r[2].strip() if len(r) > 2 else "") == expected_key for r in rows)


def append_failure(workflow: str, stage: str, error: str, note: str = "") -> bool:
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    key = run_key()
    repo = os.environ.get("GITHUB_REPOSITORY", "priihigashi/oak-park-ai-hub")
    # The URL takes the bare run id -- GitHub's run page has no per-attempt path
    # in this form -- while the stored key carries the attempt.
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}" if run_id else ""
    row = [
        datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        workflow,
        key or "—",
        stage,
        (error or "job failed — see run log")[:500],
        run_url,
        "",       # RESOLVED — intentionally blank; that is what makes it show up
        note[:300],
    ]
    token = _access_token()
    if not token:
        return False
    if not _header_ok(token):
        return False
    if _already_logged(token, key, stage):
        print(f"[log_workflow_failure] already logged for {key} / "
              f"stage {stage} — skipping duplicate")
        return True
    tab = urllib.parse.quote(FAILURES_TAB, safe="")
    # RAW, never USER_ENTERED. USER_ENTERED parses values the way typing into
    # the UI does, so an error string beginning "=" becomes a formula and an
    # error beginning "+" or "-" can be coerced or rejected outright. The ERROR
    # column carries arbitrary exception text; it must be stored, not evaluated.
    url = (f"https://sheets.googleapis.com/v4/spreadsheets/{FAILURES_SHEET_ID}"
           f"/values/{tab}!A:H:append"
           f"?valueInputOption=RAW&insertDataOption=INSERT_ROWS")
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
    # KRM #15: the append receipt is the tool reporting itself healthy. Read the
    # row back out of the sheet before believing it.
    if not _readback_matches(token, updated, key or "—"):
        print(f"[log_workflow_failure] READBACK FAILED: {updated} does not "
              f"contain {key or '—'} — treat this failure as UNLOGGED",
              file=sys.stderr)
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--error", default="")
    ap.add_argument("--note", default="")
    args = ap.parse_args()
    logged = False
    try:
        logged = append_failure(args.workflow, args.stage, args.error, args.note)
    except Exception as exc:  # best-effort: never mask the real job failure
        print(f"[log_workflow_failure] non-fatal: {exc}", file=sys.stderr)
    # The logger failing silently is what produced the false all-clear this file
    # exists to end. Still exit 0 (the job is already red for its own reason),
    # but emit a greppable marker so a log scan and the watchdog can both see
    # that this failure never reached the tab.
    if not logged:
        print("::warning title=Pipeline failure NOT logged::"
              f"LOG_FAILURE_UNLOGGED workflow={args.workflow} stage={args.stage} "
              f"run={os.environ.get('GITHUB_RUN_ID', '?')}", file=sys.stderr)
    return 0  # always 0 — the job is already failing for its own reason


if __name__ == "__main__":
    raise SystemExit(main())
