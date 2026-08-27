#!/usr/bin/env python3
"""Append ONE row to any Google Sheet tab. Composio-independent.

Auth: SHEETS_TOKEN (GitHub Secret, same shape used by build_carousel_cloud.py)
      or SHEETS_TOKEN_PATH for a local sheets_token.json.

Usage:
  python3 scripts/sheet_append_row.py \
      --sheet-id <spreadsheetId> --tab "All Docs" \
      --values "col a" "col b" "col c"

Appends only. Never clears, never overwrites. Prints the updatedRange the API
actually wrote so the tab can be verified (Known Repeat Mistake #18).
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request
from pathlib import Path

API = "https://sheets.googleapis.com/v4/spreadsheets"


def get_token() -> str:
    raw = os.environ.get("SHEETS_TOKEN", "")
    if not raw:
        path = os.environ.get("SHEETS_TOKEN_PATH", "")
        if path and Path(path).expanduser().exists():
            raw = Path(path).expanduser().read_text()
    if not raw:
        raise RuntimeError("No SHEETS_TOKEN env var or SHEETS_TOKEN_PATH set")
    td = json.loads(raw)
    data = urllib.parse.urlencode({
        "client_id": td["client_id"],
        "client_secret": td["client_secret"],
        "refresh_token": td["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    resp = json.loads(urllib.request.urlopen(
        urllib.request.Request("https://oauth2.googleapis.com/token", data=data)).read())
    return resp["access_token"]


def append_row(sheet_id: str, tab: str, values: list[str], token: str) -> dict:
    # Tab-qualified range — an unqualified range silently targets the first
    # visible sheet instead of the tab you meant.
    rng = urllib.parse.quote(f"{tab}!A:A", safe="")
    url = (f"{API}/{sheet_id}/values/{rng}:append"
           "?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS")
    req = urllib.request.Request(
        url, method="POST",
        data=json.dumps({"values": [values]}).encode(),
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet-id", required=True)
    ap.add_argument("--tab", required=True)
    ap.add_argument("--values", required=True, nargs="+")
    a = ap.parse_args()

    try:
        out = append_row(a.sheet_id, a.tab, a.values, get_token())
    except urllib.error.HTTPError as e:
        print(f"ERROR {e.code}: {e.read().decode()[:500]}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    wrote = out.get("updates", {}).get("updatedRange", "?")
    print(f"OK appended -> {wrote}")
    if not wrote.startswith(a.tab) and f"'{a.tab}'" not in wrote:
        print(f"WARNING: wrote to {wrote}, not tab {a.tab!r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
