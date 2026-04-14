#!/usr/bin/env python3
"""
drive_route_file.py — Route a file from My Drive to the correct topic shared drive
and drop a shortcut into the cross-reference working folder.

Inputs (env vars from workflow):
  INPUT_FILENAME  — name (or substring) of a file currently in My Drive root
  INPUT_TOPIC     — one of: stocks | news | opc | marketing | higashi

Flow:
  1. Find file in My Drive by name (most recently modified match)
  2. Move to the topic's destination folder (shared drive root or subfolder)
  3. Create a shortcut in the cross-reference folder for quick nav
  4. Print JSON summary
"""
import json
import os
import sys

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


TOPICS = {
    "stocks": {
        "dest_drive_id": "0AF6S_f8PH2_aUk9PVA",
        "dest_folder_id": "0AF6S_f8PH2_aUk9PVA",
        "shortcut_folder_id": "1JFndBkUh6Bac6MD7JKgIns2xgO188b1T",
    },
    "news": {
        "dest_drive_id": "0AH7_C87G0ZwgUk9PVA",
        "dest_folder_id": "0AH7_C87G0ZwgUk9PVA",
        "shortcut_folder_id": None,
    },
    "opc": {
        "dest_drive_id": "0AJp3Phs0wIBOUk9PVA",
        "dest_folder_id": "0AJp3Phs0wIBOUk9PVA",
        "shortcut_folder_id": None,
    },
    "higashi": {
        "dest_drive_id": "0AN7aea2IZzE0Uk9PVA",
        "dest_folder_id": "1CKWTojSg2uQmXjNnKlAaSBCTfxtSQBvH",
        "shortcut_folder_id": None,
    },
    "marketing": {
        "dest_drive_id": "0AIPzwsJD_qqzUk9PVA",
        "dest_folder_id": "0AIPzwsJD_qqzUk9PVA",
        "shortcut_folder_id": None,
    },
}


def build_drive():
    token_json = os.environ.get("SHEETS_TOKEN")
    if not token_json:
        raise SystemExit("SHEETS_TOKEN env var missing")
    info = json.loads(token_json)
    creds = Credentials.from_authorized_user_info(info, info.get("scopes"))
    if not creds.valid:
        creds.refresh(Request())
    return build("drive", "v3", credentials=creds)


def find_in_my_drive(svc, filename):
    q = (
        f"name contains '{filename}' and trashed=false "
        f"and 'me' in owners"
    )
    r = svc.files().list(
        q=q,
        fields="files(id,name,parents,mimeType,modifiedTime,owners(emailAddress))",
        orderBy="modifiedTime desc",
        pageSize=10,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = r.get("files", [])
    if not files:
        raise SystemExit(f"No file matching '{filename}' in My Drive")
    return files[0]


def move_to_destination(svc, file_id, current_parents, dest_folder_id):
    return svc.files().update(
        fileId=file_id,
        addParents=dest_folder_id,
        removeParents=",".join(current_parents) if current_parents else None,
        supportsAllDrives=True,
        fields="id,name,parents,driveId,webViewLink",
    ).execute()


def create_shortcut(svc, target_id, target_name, shortcut_folder_id):
    body = {
        "name": target_name,
        "mimeType": "application/vnd.google-apps.shortcut",
        "parents": [shortcut_folder_id],
        "shortcutDetails": {"targetId": target_id},
    }
    return svc.files().create(
        body=body,
        fields="id,name,parents,webViewLink,shortcutDetails",
        supportsAllDrives=True,
    ).execute()


def main():
    filename = os.environ.get("INPUT_FILENAME", "").strip()
    topic = os.environ.get("INPUT_TOPIC", "").strip().lower()

    if not filename:
        raise SystemExit("INPUT_FILENAME required")
    if topic not in TOPICS:
        raise SystemExit(f"INPUT_TOPIC must be one of {list(TOPICS)}")

    cfg = TOPICS[topic]
    svc = build_drive()

    src = find_in_my_drive(svc, filename)
    print(f"[FOUND] {src['name']} | {src['id']} | parents={src.get('parents')}")

    moved = move_to_destination(svc, src["id"], src.get("parents", []), cfg["dest_folder_id"])
    print(f"[MOVED] {moved['name']} -> drive {moved.get('driveId')} parents={moved.get('parents')}")

    shortcut = None
    if cfg["shortcut_folder_id"]:
        shortcut = create_shortcut(svc, src["id"], src["name"], cfg["shortcut_folder_id"])
        print(f"[SHORTCUT] {shortcut['id']} in folder {cfg['shortcut_folder_id']}")

    result = {
        "status": "ok",
        "file_id": src["id"],
        "file_name": src["name"],
        "topic": topic,
        "dest_folder_id": cfg["dest_folder_id"],
        "file_link": moved.get("webViewLink"),
        "shortcut_id": shortcut["id"] if shortcut else None,
        "shortcut_link": shortcut.get("webViewLink") if shortcut else None,
    }
    print("RESULT_JSON=" + json.dumps(result))


if __name__ == "__main__":
    main()
