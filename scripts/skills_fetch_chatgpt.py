#!/usr/bin/env python3
"""Download every file inside <Skill>/ChatGPT on Drive into chatgpt_dump/<Skill>/ (read-only)."""
import io
import json
import os

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

CLAUDE_COLONIZATION_ID = "1ALmXAw8nzQcEmDbFa2MTha6gLe3sqsjB"
FOLDER = "application/vnd.google-apps.folder"
A = dict(supportsAllDrives=True)
L = dict(supportsAllDrives=True, includeItemsFromAllDrives=True, corpora="allDrives")
info = json.loads(os.environ["SHEETS_TOKEN"])
creds = Credentials.from_authorized_user_info(info, info.get("scopes"))
if not creds.valid:
    creds.refresh(Request())
drive = build("drive", "v3", credentials=creds)


def children(parent):
    out, tok = [], None
    while True:
        r = drive.files().list(q=f"'{parent}' in parents and trashed=false", pageToken=tok,
                               fields="nextPageToken,files(id,name,mimeType,size)", pageSize=200, **L).execute()
        out += r["files"]
        tok = r.get("nextPageToken")
        if not tok:
            return out


def dump(fid, path):
    for f in children(fid):
        p = os.path.join(path, f["name"])
        if f["mimeType"] == FOLDER:
            dump(f["id"], p)
            continue
        os.makedirs(path, exist_ok=True)
        if f["mimeType"].startswith("application/vnd.google-apps"):
            req = drive.files().export_media(fileId=f["id"], mimeType="text/plain")
            p += ".txt"
        else:
            req = drive.files().get_media(fileId=f["id"], **A)
        buf = io.FileIO(p, "wb")
        dl = MediaIoBaseDownload(buf, req)
        done = False
        while not done:
            _, done = dl.next_chunk()
        print(p, os.path.getsize(p))


sk = drive.files().get(fileId=CLAUDE_COLONIZATION_ID, fields="parents", **A).execute()["parents"][0]
root = drive.files().get(fileId=sk, fields="parents", **A).execute()["parents"][0]
for skill in children(root):
    if skill["mimeType"] != FOLDER:
        continue
    for sub in children(skill["id"]):
        if sub["mimeType"] == FOLDER and sub["name"].lower() in ("chatgpt", "improved"):
            dump(sub["id"], os.path.join("chatgpt_dump", skill["name"], sub["name"]))
# trigger snapshot
