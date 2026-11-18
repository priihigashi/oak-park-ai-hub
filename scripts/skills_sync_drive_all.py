#!/usr/bin/env python3
"""Upload skills/<slug>/claude/* into Drive: Skills de Reels e Carrosséis > <Name> > Claude.

Mapping slug -> Drive folder name in skills/reels_skills_map.json.
Only touches the Claude subfolder (never ChatGPT/Improved). Appends one row per
skill to the Skills Tracker. All calls use supportsAllDrives=True.
"""
import datetime
import json
import os
import sys
import unicodedata

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CLAUDE_COLONIZATION_ID = "1ALmXAw8nzQcEmDbFa2MTha6gLe3sqsjB"
FOLDER = "application/vnd.google-apps.folder"
A = dict(supportsAllDrives=True)
L = dict(supportsAllDrives=True, includeItemsFromAllDrives=True, corpora="allDrives")

info = json.loads(os.environ["SHEETS_TOKEN"])
creds = Credentials.from_authorized_user_info(info, info.get("scopes"))
if not creds.valid:
    creds.refresh(Request())
drive = build("drive", "v3", credentials=creds)
sheets = build("sheets", "v4", credentials=creds)
report = {"skills": {}, "errors": []}


def norm(s):
    return unicodedata.normalize("NFC", s).strip().lower()


def children(parent):
    out, tok = [], None
    while True:
        r = drive.files().list(q=f"'{parent}' in parents and trashed=false", pageToken=tok,
                               fields="nextPageToken,files(id,name,mimeType,size,webViewLink)",
                               pageSize=200, **L).execute()
        out += r["files"]
        tok = r.get("nextPageToken")
        if not tok:
            return out


def ensure_folder(parent, name):
    for f in children(parent):
        if f["mimeType"] == FOLDER and norm(f["name"]) == norm(name):
            return f["id"]
    return drive.files().create(body={"name": name, "mimeType": FOLDER, "parents": [parent]},
                                fields="id", **A).execute()["id"]


def upload(parent, local):
    name = os.path.basename(local)
    mime = "text/markdown" if name.endswith(".md") else "application/octet-stream"
    media = MediaFileUpload(local, mimetype=mime, resumable=False)
    ex = [f for f in children(parent) if f["name"] == name and f["mimeType"] != FOLDER]
    if ex:
        fid = drive.files().update(fileId=ex[0]["id"], media_body=media, fields="id", **A).execute()["id"]
    else:
        fid = drive.files().create(body={"name": name, "parents": [parent]}, media_body=media,
                                   fields="id", **A).execute()["id"]
    return drive.files().get(fileId=fid, fields="id,name,size,webViewLink", **A).execute()


skill_folder = drive.files().get(fileId=CLAUDE_COLONIZATION_ID, fields="parents", **A).execute()["parents"][0]
root_id = drive.files().get(fileId=skill_folder, fields="parents", **A).execute()["parents"][0]
root_children = children(root_id)

mapping = json.load(open("skills/reels_skills_map.json"))
rows = []
today = datetime.date.today().isoformat()
for slug, name in mapping.items():
    match = [f for f in root_children if f["mimeType"] == FOLDER and norm(f["name"]) == norm(name)]
    if not match:
        report["errors"].append(f"Drive folder not found: {name}")
        continue
    claude_id = ensure_folder(match[0]["id"], "Claude")
    files = []
    local_dir = f"skills/{slug}/claude"
    for fn in sorted(os.listdir(local_dir)):
        f = upload(claude_id, os.path.join(local_dir, fn))
        files.append(f)
        if int(f.get("size", 0)) <= 0:
            report["errors"].append(f"EMPTY on Drive: {slug}/{fn}")
    report["skills"][name] = {"claude_folder": f"https://drive.google.com/drive/folders/{claude_id}",
                              "files": files}
    rows.append([today, "Claude", f"{name} ({slug})",
                 "Cópia inicial do SKILL.md do Claude com aviso dos 3 lugares",
                 "Mac + Drive + GitHub", "Concluído"])

tracker = [f for f in root_children if f["name"] == "Skills Tracker"]
if tracker and rows:
    sheets.spreadsheets().values().append(
        spreadsheetId=tracker[0]["id"], range="A1", valueInputOption="RAW",
        insertDataOption="INSERT_ROWS", body={"values": rows}).execute()
elif rows:
    report["errors"].append("Skills Tracker not found")

print(json.dumps(report, indent=2, ensure_ascii=False))
sys.exit(1 if report["errors"] else 0)
