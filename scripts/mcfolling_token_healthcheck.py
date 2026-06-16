#!/usr/bin/env python3
"""
OAuth token health-check — early-warning for the 7-day Testing-mode token death.

Background (memory: project_oauth_token_expiry_fix.md):
  The nano Project OAuth app is in "Testing" publishing status, so Google expires
  refresh tokens after ~7 days. Tokens for McFolling and the Google Ads dashboard
  keep dying with `invalid_grant`. The PERMANENT fix is publishing the app to
  Production (Priscila, one-time). Until then, this script ATTEMPTS A LIVE REFRESH
  of each token daily so we get an email the morning a token dies — instead of
  discovering it mid-task.

It does NOT prevent the expiry. It only detects it early.

Behaviour:
  - Reads each token from an env var holding the token JSON (authorized_user shape).
  - Tries creds.refresh(Request()). Success = token alive.
  - Prints a per-token line. Exits NON-ZERO if ANY token failed to refresh, so the
    GitHub Actions run flips red and the `if: failure()` email step fires.

Env vars (each = full token JSON string, same shape as the *_token.json files):
  MCFOLLING_TOKEN  (required)
  SHEETS_TOKEN     (optional — Priscila/OPC + ads dashboard token; checked if present)
"""

import json
import os
import sys

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# (env var name, human label, required?)
TOKENS = [
    ("MCFOLLING_TOKEN", "McFolling (mcfollingproperties@gmail.com)", True),
    ("SHEETS_TOKEN", "Priscila/OPC + Google Ads dashboard", False),
]


def check_token(env_name: str, label: str, required: bool) -> tuple[bool, str]:
    raw = os.environ.get(env_name, "").strip()
    if not raw:
        if required:
            return False, f"❌ {label}: env var {env_name} is empty/missing"
        return True, f"⏭️  {label}: {env_name} not set — skipped (optional)"

    try:
        info = json.loads(raw)
    except json.JSONDecodeError as e:
        return False, f"❌ {label}: {env_name} is not valid JSON ({e})"

    try:
        creds = Credentials.from_authorized_user_info(info)
    except Exception as e:  # noqa: BLE001
        return False, f"❌ {label}: could not build credentials ({e})"

    try:
        creds.refresh(Request())
    except Exception as e:  # noqa: BLE001 — refresh raises RefreshError on invalid_grant
        return False, f"❌ {label}: refresh FAILED — {type(e).__name__}: {e}"

    return True, f"✅ {label}: token alive (refresh succeeded)"


def main() -> int:
    print("OAuth token health-check\n" + "=" * 40)
    all_ok = True
    for env_name, label, required in TOKENS:
        ok, msg = check_token(env_name, label, required)
        print(msg)
        if not ok:
            all_ok = False

    print("=" * 40)
    if all_ok:
        print("RESULT: all tokens healthy")
        return 0

    print(
        "RESULT: one or more tokens DEAD.\n"
        "Fix now → re-auth (python3 ~/ClaudeWorkspace/Credentials/authorize_mcfolling.py), "
        "then: gh secret set MCFOLLING_TOKEN < mcfolling_token.json\n"
        "PERMANENT fix → publish the OAuth app: Google Cloud Console > APIs & Services > "
        "OAuth consent screen > Publish App (Testing -> Production)."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
