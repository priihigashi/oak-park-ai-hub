#!/usr/bin/env python3
"""
sync_shortcuts.py — Syncs Drive Shortcuts folders for Brazil, USA, OPC.

Rules:
  Carousels/ — one shortcut per static version folder (v<N>_<slug>, NOT _motion).
               Shortcut points to the png/ subfolder so opening it shows slides immediately.
  Videos/    — one shortcut per cover MP4 file found inside any version folder's motion/
               subfolder. Shortcut points to the FILE (not the folder) so Drive plays inline.

Run: python scripts/shortcuts/sync_shortcuts.py
Env: SHEETS_TOKEN (Google OAuth JSON)
"""
import json, os, re, sys, urllib.request, urllib.parse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

VERSION_RE   = re.compile(r'^v\d+_(?!.*_motion$)')   # static only — excludes _motion siblings
MOTION_RE    = re.compile(r'^v\d+_.*_motion$')        # _motion sibling folders (skip for carousels)

# Niche roots — folder scanned recursively for version folders
NICHE_ROOTS = {
    "brazil": "1QVLhs-xJcmG1YhpysZQm17JhGhjkRTUZ",  # News > Brazil
    "usa":    "1I6sm86NBABrWvgY4vkWpSwaeSIRpwpth",  # News > USA
    "opc":    "12WR29-Vg6KdFq2XwTs2exZirsXG-RyrC",  # Marketing > Oak Park Construction
}

# Shortcuts destination folders (created 2026-04-17)
SHORTCUT_FOLDERS = {
    "brazil": {
        "root":      "1-kzEeGvPZSTV7li4cjDYSGNkstfvlf_m",
        "carousels": "1texYwliSc2eJjjVxSmY3bfV-f39USbJg",
        "videos":    "1d5lJi5exZK_vhNVB6MWyjdFotMBBgPVd",
    },
    "usa": {
        "root":      "16Q7EzQOEFStfmpXUFEcd64mHdD-ErO7x",
        "carousels": "1jPB6TjbV8Bu2k3zeN3uT7EIvspwIrWtQ",
        "videos":    "126K6N9UDOFj_zS-h3e4dD30GwZOviugT",
    },
    "opc": {
        "root":      "11D_QYDEt6x4pZv791r9OlLco3ayRGFDR",
        "carousels": "13pqneqeDy1-LAtGsRJDg9gmNl07Ye41g",
        "videos":    "1LKS51EfDxrR3ib6TsR2DADMpt3der36D",
    },
}


def _auth():
    raw = os.environ.get("SHEETS_TOKEN", "")
    if not raw:
        print("ERROR: SHEETS_TOKEN not set"); sys.exit(1)
    td = json.loads(raw)
    data = urllib.parse.urlencode({
        "client_id": td["client_id"], "client_secret": td["client_secret"],
        "refresh_token": td["refresh_token"], "grant_type": "refresh_token",
    }).encode()
    resp = json.loads(urllib.request.urlopen(
        urllib.request.Request("https://oauth2.googleapis.com/token", data=data)).read())
    return Credentials(
        token=resp["access_token"], refresh_token=td["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=td["client_id"], client_secret=td["client_secret"],
    )


def _ls(drive, parent_id, mime=None):
    q = f"'{parent_id}' in parents and trashed=false"
    if mime:
        q += f" and mimeType='{mime}'"
    return drive.files().list(
        q=q, supportsAllDrives=True, includeItemsFromAllDrives=True,
        corpora="allDrives", fields="files(id,name,mimeType,shortcutDetails)"
    ).execute().get("files", [])


def _find_version_folders(drive, root_id, skip_ids, depth=0):
    """Recursively find all static version folders (v<N>_slug, not _motion)."""
    if depth > 6:
        return []
    found = []
    for f in _ls(drive, root_id, mime="application/vnd.google-apps.folder"):
        if f["id"] in skip_ids:
            continue
        if VERSION_RE.match(f["name"]):
            found.append(f)
        elif not MOTION_RE.match(f["name"]):
            found.extend(_find_version_folders(drive, f["id"], skip_ids, depth + 1))
    return found


def _existing_targets(drive, folder_id):
    """Return set of targetIds already shortcutted in a folder."""
    targets = set()
    for f in _ls(drive, folder_id):
        td = (f.get("shortcutDetails") or {}).get("targetId")
        if td:
            targets.add(td)
    return targets


def _make_shortcut(drive, target_id, name, dest_id):
    drive.files().create(
        body={"name": name, "mimeType": "application/vnd.google-apps.shortcut",
              "shortcutDetails": {"targetId": target_id}, "parents": [dest_id]},
        supportsAllDrives=True, fields="id",
    ).execute()


def sync_niche(drive, niche, root_id, sc):
    print(f"\n=== {niche.upper()} ===")
    skip = {sc["root"], sc["carousels"], sc["videos"]}

    existing_carousels = _existing_targets(drive, sc["carousels"])
    existing_videos    = _existing_targets(drive, sc["videos"])

    version_folders = _find_version_folders(drive, root_id, skip)
    print(f"  Found {len(version_folders)} static version folders")

    for vf in version_folders:
        # ── CAROUSELS: shortcut to png/ subfolder ────────────────────────────
        if vf["id"] not in existing_carousels:
            png_folders = _ls(drive, vf["id"], mime="application/vnd.google-apps.folder")
            png_sub = next((f["id"] for f in png_folders if f["name"] == "png"), None)
            if png_sub:
                _make_shortcut(drive, png_sub, vf["name"], sc["carousels"])
                print(f"  ✅ Carousel: {vf['name']} → png/")
            else:
                # No png/ subfolder — PNGs are at root, shortcut to version folder itself
                _make_shortcut(drive, vf["id"], vf["name"], sc["carousels"])
                print(f"  ✅ Carousel: {vf['name']} → (root PNGs)")
        else:
            print(f"  — Carousel already exists: {vf['name']}")

        # ── VIDEOS: shortcut to cover MP4 file in motion/ subfolder ──────────
        motion_subs = [f for f in _ls(drive, vf["id"], mime="application/vnd.google-apps.folder")
                       if f["name"] == "motion"]
        for motion_sub in motion_subs:
            mp4s = drive.files().list(
                q=f"'{motion_sub['id']}' in parents and mimeType='video/mp4' and trashed=false",
                supportsAllDrives=True, includeItemsFromAllDrives=True,
                fields="files(id,name)"
            ).execute().get("files", [])
            cover_mp4 = next((f for f in mp4s if "cover" in f["name"].lower()), mp4s[0] if mp4s else None)
            if cover_mp4 and cover_mp4["id"] not in existing_videos:
                _make_shortcut(drive, cover_mp4["id"], vf["name"], sc["videos"])
                print(f"  ✅ Video: {vf['name']} → {cover_mp4['name']}")
                existing_videos.add(cover_mp4["id"])


def main():
    drive = build("drive", "v3", credentials=_auth())
    for niche, root_id in NICHE_ROOTS.items():
        sync_niche(drive, niche, root_id, SHORTCUT_FOLDERS[niche])
    print("\nSync complete.")


if __name__ == "__main__":
    main()
