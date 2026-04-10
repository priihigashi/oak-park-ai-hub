#!/usr/bin/env python3
"""
archive_cleanup.py — Oak Park Construction
Runs monthly on the 1st via GitHub Actions.

Scans the 'Weekly Reports' Drive folder for docs older than 6 months.
If any are found, sends an email to Priscila asking if they can be deleted.
Logs all checks to a tracking spreadsheet tab.

Env vars required:
  SHEETS_TOKEN          — Google OAuth token JSON (needs Drive + Gmail scope)
  ARCHIVE_FOLDER_ID     — Drive folder ID to scan (Weekly Reports)
  NOTIFY_EMAIL          — Email address to notify (priscila@oakpark-construction.com)
  CONTENT_SHEET_ID      — Optional: sheet ID for logging (uses CONTENT_SHEET_ID secret)
"""

import os, json, urllib.request, urllib.parse, sys, time, base64
from datetime import datetime, timedelta, timezone
import pytz

# ── Config ──────────────────────────────────────────────────────────────────
FOLDER_ID    = os.environ.get("ARCHIVE_FOLDER_ID", "1gETNHiEtbkjYRimJOccDR9zssWSM4vNM")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "priscila@oakpark-construction.com")
SHEET_ID     = os.environ.get("CONTENT_SHEET_ID", "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU")
LOG_TAB      = "🗂️ Archive Cleanup Log"
SIX_MONTHS   = 180  # days

ET = pytz.timezone("America/New_York")

# ── Auth ───────────────────────────────────────────────────────────────────
_token_cache = {}

def get_token():
    if _token_cache.get("token") and time.time() < _token_cache.get("exp", 0):
        return _token_cache["token"]
    raw = os.environ.get("SHEETS_TOKEN", "")
    if not raw:
        raise RuntimeError("No SHEETS_TOKEN set")
    td = json.loads(raw)
    data = urllib.parse.urlencode({
        "client_id":     td["client_id"],
        "client_secret": td["client_secret"],
        "refresh_token": td["refresh_token"],
        "grant_type":    "refresh_token",
    }).encode()
    resp = json.loads(urllib.request.urlopen(
        urllib.request.Request("https://oauth2.googleapis.com/token", data=data)).read())
    _token_cache["token"] = resp["access_token"]
    _token_cache["exp"]   = time.time() + resp.get("expires_in", 3500) - 60
    return resp["access_token"]

def api(url, method="GET", body=None, token=None):
    t = token or get_token()
    headers = {"Authorization": f"Bearer {t}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"  ⚠️  HTTP {e.code}: {e.read().decode()[:300]}")
        return None

# ── Drive: list files in folder ─────────────────────────────────────────────
def list_files_in_folder(folder_id):
    q = urllib.parse.quote(f"'{folder_id}' in parents and trashed = false and mimeType = 'application/vnd.google-apps.document'")
    url = f"https://www.googleapis.com/drive/v3/files?q={q}&fields=files(id,name,createdTime,webViewLink)&supportsAllDrives=true&includeItemsFromAllDrives=true&pageSize=100"
    resp = api(url)
    return resp.get("files", []) if resp else []

# ── Sheets: log run ─────────────────────────────────────────────────────────
def ensure_log_tab():
    meta = api(f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}?fields=sheets.properties.title")
    if not meta:
        return False
    tabs = [s["properties"]["title"] for s in meta.get("sheets", [])]
    if LOG_TAB in tabs:
        return True
    body = {"requests": [{"addSheet": {"properties": {"title": LOG_TAB}}}]}
    api(f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}:batchUpdate", "POST", body)
    # Add header
    api(f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(LOG_TAB)}!A1:E1:append?valueInputOption=USER_ENTERED", "POST",
        {"values": [["Run Date", "Files Scanned", "Old Files Found", "Email Sent", "Files Listed"]]})
    return True

def log_run(files_scanned, old_files, email_sent, file_names):
    ensure_log_tab()
    now = datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")
    names = " | ".join([f["name"] for f in file_names]) if file_names else "none"
    tab_enc = urllib.parse.quote(LOG_TAB)
    api(f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{tab_enc}!A:E:append?valueInputOption=USER_ENTERED", "POST",
        {"values": [[now, str(files_scanned), str(old_files), "Yes" if email_sent else "No", names]]})

# ── Gmail: send notification email ─────────────────────────────────────────
def send_email(old_files):
    subject = f"[Archive Cleanup] {len(old_files)} Weekly Report(s) are 6+ months old — OK to delete?"
    lines = ["Hi Priscila,", "",
             f"The archive cleanup script found {len(old_files)} Weekly Report doc(s) older than 6 months:",
             ""]
    for f in old_files:
        created = f.get("createdTime", "unknown")[:10]
        lines.append(f"  - {f['name']}  (created {created})")
        lines.append(f"    Link: {f.get('webViewLink', 'N/A')}")
        lines.append("")
    lines += [
        "Reply to this email or tell Claude: 'delete old weekly reports' to remove them.",
        "Or ignore this email to keep them.",
        "",
        "— Oak Park AI System (archive_cleanup.py)"
    ]
    body_text = "\n".join(lines)

    # Encode as RFC 2822 message
    msg = f"From: {NOTIFY_EMAIL}\r\nTo: {NOTIFY_EMAIL}\r\nSubject: {subject}\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n{body_text}"
    encoded = base64.urlsafe_b64encode(msg.encode("utf-8")).decode("utf-8")

    resp = api("https://gmail.googleapis.com/gmail/v1/users/me/messages/send", "POST",
               {"raw": encoded})
    if resp and resp.get("id"):
        print(f"  ✅ Email sent (id: {resp['id']})")
        return True
    else:
        print("  ⚠️  Gmail send failed — check token has gmail.send scope")
        # Fallback: print to stdout so GitHub Actions logs it
        print("\n" + "="*60)
        print("ARCHIVE NOTIFICATION (email failed, logged here instead):")
        print(body_text)
        print("="*60 + "\n")
        return False

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    print(f"\n📁 Archive Cleanup — {datetime.now(ET).strftime('%Y-%m-%d')}")
    print(f"   Folder: {FOLDER_ID}")
    print(f"   Threshold: {SIX_MONTHS} days (6 months)\n")

    files = list_files_in_folder(FOLDER_ID)
    print(f"   Found {len(files)} doc(s) in Weekly Reports folder")

    cutoff = datetime.now(timezone.utc) - timedelta(days=SIX_MONTHS)
    old_files = []
    for f in files:
        created_str = f.get("createdTime", "")
        if not created_str:
            continue
        created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - created_dt).days
        print(f"   - {f['name']}  ({age_days}d old)")
        if created_dt < cutoff:
            old_files.append(f)

    if not old_files:
        print(f"\n  ✅ No docs older than {SIX_MONTHS} days. Nothing to clean up.")
        log_run(len(files), 0, False, [])
        return

    print(f"\n  ⚠️  {len(old_files)} doc(s) are 6+ months old — sending email\n")
    email_sent = send_email(old_files)
    log_run(len(files), len(old_files), email_sent, old_files)
    print(f"\n  Done. Run logged to '{LOG_TAB}' tab.")

if __name__ == "__main__":
    main()
