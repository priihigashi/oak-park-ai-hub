#!/usr/bin/env python3
"""
upload_reels.py — Upload rendered Remotion MP4 reels to News drive SOVEREIGN folder.
Follows Drive OAuth pattern (supportsAllDrives=True, shared drive folder ID).
"""
import argparse
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--story-id", required=True)
    parser.add_argument("--en-reel", required=True)
    parser.add_argument("--pt-reel", required=True)
    parser.add_argument("--folder-id", required=True)
    args = parser.parse_args()

    if not args.folder_id:
        print("ERROR: --folder-id is empty. Set SOVEREIGN_TEMPLATE_FOLDER secret.", file=sys.stderr)
        sys.exit(1)

    token_data = json.loads(os.environ.get("SHEETS_TOKEN", "{}"))
    if not token_data:
        print("ERROR: SHEETS_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
    )
    drive = build("drive", "v3", credentials=creds)

    # Create version subfolder: v1_regime-change/ (or next version)
    slug = args.story_id.lower().replace("-", "_")
    version_folder_meta = {
        "name": f"v1_{slug}_motion",
        "parents": [args.folder_id],
        "mimeType": "application/vnd.google-apps.folder",
    }
    version_folder = drive.files().create(
        body=version_folder_meta, supportsAllDrives=True, fields="id,webViewLink"
    ).execute()
    folder_id = version_folder["id"]
    folder_link = version_folder.get("webViewLink", "")
    print(f"Version folder: {folder_link}")

    # Upload both reels
    for reel_path, lang in [(args.en_reel, "en"), (args.pt_reel, "pt")]:
        if not os.path.exists(reel_path):
            print(f"WARNING: {reel_path} not found, skipping {lang} upload")
            continue
        size_mb = os.path.getsize(reel_path) / (1024 * 1024)
        print(f"Uploading {lang} reel ({size_mb:.1f} MB)...")
        file_meta = {
            "name": f"{args.story_id}_reel_{lang}.mp4",
            "parents": [folder_id],
        }
        media = MediaFileUpload(reel_path, mimetype="video/mp4", resumable=True)
        result = drive.files().create(
            body=file_meta, media_body=media, supportsAllDrives=True, fields="id,webViewLink"
        ).execute()
        print(f"  {lang} reel: {result.get('webViewLink', result['id'])}")

    print(f"\nAll reels uploaded to: {folder_link}")


if __name__ == "__main__":
    main()
