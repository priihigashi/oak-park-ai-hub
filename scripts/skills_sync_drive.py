#!/usr/bin/env python3
"""Mirror skills/colonization-br/<version>/ from this repo to Google Drive.

Drive layout: Skills de Reels e Carrosséis > Colonization BR > Claude|ChatGPT|Improved
Also uploads README.md to the Skills de Reels e Carrosséis folder and keeps the
append-only "Skills Tracker" Google Sheet there. Prints a JSON report.
Every Drive call uses supportsAllDrives=True. OAuth token from SHEETS_TOKEN.
"""
import datetime
import json
import mimetypes
import os
import sys

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CLAUDE_FOLDER_ID = "1ALmXAw8nzQcEmDbFa2MTha6gLe3sqsjB"  # Colonization BR > Claude
LOCAL_SKILL = "skills/colonization-br"
VERSION_MAP = {"claude": "Claude", "chatgpt": "ChatGPT", "improved": "Improved"}
TRACKER_NAME = "Skills Tracker"
HEADERS = ["Data", "Quem (Claude/ChatGPT)", "Skill", "O que mudou",
           "Onde atualizou (Mac/Drive/GitHub)", "Status"]
FOLDER = "application/vnd.google-apps.folder"
A = dict(supportsAllDrives=True)
L = dict(supportsAllDrives=True, includeItemsFromAllDrives=True, corpora="allDrives")

info = json.loads(os.environ["SHEETS_TOKEN"])
creds = Credentials.from_authorized_user_info(info, info.get("scopes"))
if not creds.valid:
    creds.refresh(Request())
drive = build("drive", "v3", credentials=creds)
sheets = build("sheets", "v4", credentials=creds)
report = {"files": [], "errors": []}


def q(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")


def find(parent, name, mime=None):
    qs = f"'{parent}' in parents and name='{q(name)}' and trashed=false"
    if mime:
        qs += f" and mimeType='{mime}'"
    r = drive.files().list(q=qs, fields="files(id,name,size,mimeType,webViewLink)", **L).execute()
    return r["files"][0] if r["files"] else None


def ensure_folder(parent, name):
    f = find(parent, name, FOLDER)
    if f:
        return f["id"]
    return drive.files().create(body={"name": name, "mimeType": FOLDER, "parents": [parent]},
                                fields="id", **A).execute()["id"]


def upload(parent, local, name=None):
    name = name or os.path.basename(local)
    mime = "text/markdown" if local.endswith(".md") else (
        mimetypes.guess_type(local)[0] or "application/octet-stream")
    media = MediaFileUpload(local, mimetype=mime, resumable=False)
    ex = find(parent, name)
    if ex and ex["mimeType"] != FOLDER:
        f = drive.files().update(fileId=ex["id"], media_body=media, fields="id", **A).execute()
    else:
        f = drive.files().create(body={"name": name, "parents": [parent]}, media_body=media,
                                 fields="id", **A).execute()
    f = drive.files().get(fileId=f["id"], fields="id,name,size,webViewLink", **A).execute()
    report["files"].append({"local": local, **f})
    if int(f.get("size", 0)) <= 0:
        report["errors"].append(f"EMPTY on Drive: {local}")


def mirror(local_dir, drive_dir):
    for entry in sorted(os.listdir(local_dir)):
        if entry == ".gitkeep":
            continue
        p = os.path.join(local_dir, entry)
        if os.path.isdir(p):
            mirror(p, ensure_folder(drive_dir, entry))
        else:
            upload(drive_dir, p)


claude = drive.files().get(fileId=CLAUDE_FOLDER_ID, fields="id,name,parents,webViewLink", **A).execute()
skill_id = claude["parents"][0]
skill = drive.files().get(fileId=skill_id, fields="id,name,parents,webViewLink", **A).execute()
root_id = skill["parents"][0]
root = drive.files().get(fileId=root_id, fields="id,name,webViewLink", **A).execute()
report["folders"] = {"claude": claude, "skill": skill, "root": root}

for local_v, drive_v in VERSION_MAP.items():
    did = CLAUDE_FOLDER_ID if local_v == "claude" else ensure_folder(skill_id, drive_v)
    report["folders"][drive_v] = f"https://drive.google.com/drive/folders/{did}"
    lp = os.path.join(LOCAL_SKILL, local_v)
    if os.path.isdir(lp):
        mirror(lp, did)

upload(root_id, "skills/README_reels_carrosseis.md", "README.md")

# Skills Tracker: append-only, never overwrite
t = find(root_id, TRACKER_NAME, "application/vnd.google-apps.spreadsheet")
if not t:
    t = drive.files().create(body={"name": TRACKER_NAME, "parents": [root_id],
                                   "mimeType": "application/vnd.google-apps.spreadsheet"},
                             fields="id", **A).execute()
    sheets.spreadsheets().values().update(
        spreadsheetId=t["id"], range="A1", valueInputOption="RAW",
        body={"values": [HEADERS]}).execute()
note = os.environ.get("TRACKER_NOTE") or (
    "Espelhamento inicial: SKILL.md com aviso dos 3 lugares, README, pastas Claude/ChatGPT/Improved")
row = [datetime.date.today().isoformat(), "Claude", "Colonization BR (coolonizacao-br)",
       note, "Mac + Drive + GitHub", "Concluído"]
sheets.spreadsheets().values().append(
    spreadsheetId=t["id"], range="A1", valueInputOption="RAW",
    insertDataOption="INSERT_ROWS", body={"values": [row]}).execute()
report["tracker"] = drive.files().get(fileId=t["id"], fields="id,webViewLink", **A).execute()

print(json.dumps(report, indent=2, ensure_ascii=False))
sys.exit(1 if report["errors"] else 0)
