"""
chat_log_reader.py — Reads recent Chat Logs from Drive, extracts carry-forward items.
Chat Logs folder: 1qitnbz5_8tfZI2rnTogV1zLLLLOwFVCw
Log naming: LOG_YYYY-MM-DD_HHMM

Cost gate:
  Tier 1 (free)  — list files, compare timestamps vs state file
  Tier 2 (Haiku) — export + extract carry-forwards only if new log found

Output: carry_forwards.json + Calendar tasks + Inbox tab entries
"""
import os, json
import pytz
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2 import service_account
import anthropic

CHAT_LOGS_FOLDER = "1qitnbz5_8tfZI2rnTogV1zLLLLOwFVCw"
SPREADSHEET_ID   = "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU"
STATE_FILE       = ".github/agent_state/chat_log_state.json"
CARRIES_FILE     = ".github/agent_state/carry_forwards.json"
et               = pytz.timezone("America/New_York")
client           = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar",
]


def _creds():
    return service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GOOGLE_SA_KEY"]), scopes=SCOPES
    )


def _list_recent_logs(drive_svc, days=2):
    cutoff = (datetime.now(et) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    result = drive_svc.files().list(
        q=f"'{CHAT_LOGS_FOLDER}' in parents and name contains 'LOG_' and modifiedTime > '{cutoff}'",
        fields="files(id, name, modifiedTime)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    return result.get("files", [])


def _export_doc(drive_svc, file_id):
    try:
        content = drive_svc.files().export(
            fileId=file_id, mimeType="text/plain"
        ).execute()
        return content.decode("utf-8") if isinstance(content, bytes) else content
    except Exception as e:
        print(f"[chat_log_reader] Could not export doc {file_id}: {e}")
        return None


def _extract_carries(log_text, log_name):
    """Haiku extracts carry-forwards. Called only when new log detected."""
    prompt = f"""You are reading a session log from an AI assistant (Claude) working with Priscila.

Log: {log_name}
Content:
{log_text[:3000]}

Extract ONLY items that were promised/planned but NOT yet completed.
Look for: "carry-forward", "NOT done", "pending", "next session", "promised", "deferred".

Return ONLY valid JSON:
{{
  "carry_forwards": [
    {{
      "task": "short task description",
      "context": "why it matters",
      "auto_actionable": true
    }}
  ],
  "new_ideas": ["any new idea mentioned that should go to Inbox"],
  "source_log": "{log_name}"
}}

auto_actionable = true means Claude can create the Calendar task without asking Priscila.
Return empty arrays if nothing found."""

    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return json.loads(text)


def _create_calendar_task(calendar_svc, task, context, source_log):
    date_str = datetime.now(et).strftime("%Y-%m-%d")
    try:
        calendar_svc.events().insert(
            calendarId="primary",
            body={
                "summary":     f"🔄 CARRY: {task[:80]}",
                "description": f"{context}\n\nSource: {source_log}\nAuto-created by 4AM agent.",
                "start":       {"date": date_str},
                "end":         {"date": date_str},
                "colorId":     "6",
            },
        ).execute()
        return True
    except Exception as e:
        print(f"[chat_log_reader] Calendar task failed: {e}")
        return False


def _add_to_inbox(sheets_svc, ideas, source_log):
    if not ideas:
        return
    now  = datetime.now(et).strftime("%Y-%m-%d")
    rows = [[now, idea, "idea", source_log, "4AM-auto", "", ""] for idea in ideas]
    sheets_svc.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="📥 Inbox!A:G",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()


def run():
    """Main entry — called via runner.run_module('chat_log_reader', chat_log_reader.run)."""
    creds        = _creds()
    drive_svc    = build("drive",    "v3", credentials=creds)
    sheets_svc   = build("sheets",   "v4", credentials=creds)
    calendar_svc = build("calendar", "v3", credentials=creds)

    # Tier 1: list recent logs
    logs = _list_recent_logs(drive_svc, days=2)
    if not logs:
        print("[chat_log_reader] No new chat logs in last 48h. Zero tokens used.")
        return {"carry_forwards": [], "processed_logs": 0}

    # Load state to skip already-processed logs
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)

    all_carries = []
    processed   = 0

    for log_file in logs:
        if state.get(log_file["id"]) == log_file["modifiedTime"]:
            print(f"[chat_log_reader] Already processed: {log_file['name']}")
            continue

        print(f"[chat_log_reader] Processing: {log_file['name']}")
        text = _export_doc(drive_svc, log_file["id"])
        if not text:
            continue

        # Tier 2: Haiku extracts carry-forwards
        extracted = _extract_carries(text, log_file["name"])
        carries   = extracted.get("carry_forwards", [])
        ideas     = extracted.get("new_ideas", [])

        print(f"[chat_log_reader]   {len(carries)} carry-forwards, {len(ideas)} ideas")

        for c in carries:
            if c.get("auto_actionable"):
                _create_calendar_task(calendar_svc, c["task"], c["context"], log_file["name"])

        if ideas:
            _add_to_inbox(sheets_svc, ideas, log_file["name"])

        all_carries.extend(carries)
        state[log_file["id"]] = log_file["modifiedTime"]
        processed += 1

    # Persist state
    os.makedirs(".github/agent_state", exist_ok=True)
    with open(CARRIES_FILE, "w") as f:
        json.dump(all_carries, f, indent=2)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    print(f"[chat_log_reader] Done: {processed} logs, {len(all_carries)} carry-forwards")
    return {"carry_forwards": all_carries, "processed_logs": processed}
