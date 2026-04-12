#!/usr/bin/env python3
"""
setup_book_tracker.py
=====================
Creates a "Personal" folder in Google Drive (under Marketing) and a
"Book Tracking" spreadsheet inside it.

Columns designed to answer: "What do I want to know before buying a book?"
  - Title, Author, Genre, Pages, Price (Paperback), Price (Kindle),
    Audible (Yes/No + price), Rating, Why Read It, Status, Notes, Date Added

USAGE:
  python scripts/setup_book_tracker.py

  To also add the first book:
  python scripts/setup_book_tracker.py --seed

REQUIRED ENV VARS:
  GOOGLE_SA_KEY   — base64-encoded service account JSON
"""

import os
import sys
import json
import base64
import argparse
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Marketing parent folder — update if different
# Using Claude Code Workspace as parent since it's the working area
MARKETING_PARENT_FOLDER_ID = "1prdRT9ejOT-s-kzt0DIZ4QZuerdjv4PP"


def _get_creds():
    from google.oauth2.service_account import Credentials
    sa_b64 = os.getenv("GOOGLE_SA_KEY")
    if sa_b64:
        sa_info = json.loads(base64.b64decode(sa_b64))
        return Credentials.from_service_account_info(sa_info, scopes=[
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets",
        ])
    raise RuntimeError("GOOGLE_SA_KEY not set")


def create_folder(drive, name, parent_id):
    """Create a folder in Drive. Returns folder ID."""
    resp = drive.files().create(
        body={
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        },
        supportsAllDrives=True,
        fields="id,webViewLink",
    ).execute()
    print(f"  Folder created: {name}")
    print(f"  URL: {resp.get('webViewLink', '')}")
    return resp["id"]


def create_spreadsheet(drive, sheets_svc, name, folder_id):
    """Create a spreadsheet in the folder. Returns spreadsheet ID."""
    file = drive.files().create(
        body={
            "name": name,
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "parents": [folder_id],
        },
        supportsAllDrives=True,
        fields="id,webViewLink",
    ).execute()
    sheet_id = file["id"]
    print(f"  Spreadsheet created: {name}")
    print(f"  URL: {file.get('webViewLink', '')}")
    return sheet_id


def setup_headers(sheets_svc, spreadsheet_id):
    """Set up the Book Tracking headers and formatting."""
    headers = [
        "Title",
        "Author",
        "Genre / Category",
        "Pages",
        "Year Published",
        "Paperback Price",
        "Kindle Price",
        "Audible Available",
        "Audible Price",
        "Audible Length",
        "Narrator",
        "Goodreads Rating",
        "# of Ratings",
        "Why Read This",
        "Key Topics / Themes",
        "Difficulty Level",
        "Status",
        "My Rating",
        "Notes",
        "Date Added",
        "Source / Who Recommended",
    ]

    # Write headers
    sheets_svc.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A1",
        valueInputOption="RAW",
        body={"values": [headers]},
    ).execute()

    # Rename sheet
    sheet_props = sheets_svc.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()
    sheet_gid = sheet_props["sheets"][0]["properties"]["sheetId"]

    # Format headers (bold, freeze row, auto-resize)
    sheets_svc.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [
            # Bold headers
            {"repeatCell": {
                "range": {"sheetId": sheet_gid, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {"userEnteredFormat": {
                    "textFormat": {"bold": True},
                    "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
                }},
                "fields": "userEnteredFormat(textFormat,backgroundColor)",
            }},
            # Freeze header row
            {"updateSheetProperties": {
                "properties": {"sheetId": sheet_gid, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount",
            }},
            # Rename to "📚 Reading List"
            {"updateSheetProperties": {
                "properties": {"sheetId": sheet_gid, "title": "📚 Reading List"},
                "fields": "title",
            }},
        ]},
    ).execute()

    print("  Headers set + formatted")
    return headers


def add_seed_book(sheets_svc, spreadsheet_id):
    """Add 'A People's History of the United States' as the first entry."""
    book = [
        "A People's History of the United States",               # Title
        "Howard Zinn",                                           # Author
        "History / Political Science / Non-Fiction",             # Genre
        "729",                                                    # Pages
        "1980 (updated 2003)",                                   # Year Published
        "$15-$20",                                               # Paperback Price
        "$12.99",                                                # Kindle Price
        "Yes",                                                    # Audible Available
        "$35 (or 1 credit)",                                     # Audible Price
        "34 hours",                                               # Audible Length
        "Jeff Zinn (author's son)",                              # Narrator
        "4.1/5",                                                  # Goodreads Rating
        "~190,000+",                                              # # of Ratings
        "Tells US history from the perspective of marginalized groups — "   # Why Read
        "workers, Native Americans, enslaved people, immigrants. "
        "Challenges the standard 'great men' narrative. Controversial but "
        "widely assigned in universities.",
        "Columbus & colonization, slavery & resistance, labor movements, "  # Key Topics
        "Civil Rights, anti-war movements, class struggle, women's rights",
        "Moderate (accessible writing, college-level content)",  # Difficulty
        "Want to Read",                                           # Status
        "",                                                       # My Rating
        "Recommended by @getbetterwithbooks reel. Book is debated — "       # Notes
        "some historians praise its perspective, others criticize "
        "cherry-picking sources. Best read alongside traditional histories.",
        datetime.now().strftime("%Y-%m-%d"),                     # Date Added
        "@getbetterwithbooks (Instagram Reel)",                  # Source
    ]

    sheets_svc.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="📚 Reading List!A2",
        valueInputOption="RAW",
        body={"values": [book]},
    ).execute()
    print("  First book added: A People's History of the United States")


def main():
    parser = argparse.ArgumentParser(description="Set up Book Tracking spreadsheet")
    parser.add_argument("--seed", action="store_true", help="Add first book entry")
    parser.add_argument("--parent-folder", default=MARKETING_PARENT_FOLDER_ID,
                        help="Parent Drive folder ID")
    args = parser.parse_args()

    from googleapiclient.discovery import build
    creds = _get_creds()
    drive = build("drive", "v3", credentials=creds)
    sheets_svc = build("sheets", "v4", credentials=creds)

    print("\n=== Setting up Book Tracking ===\n")

    # 1. Create Personal folder
    print("[1/3] Creating 'Personal' folder...")
    personal_folder_id = create_folder(drive, "Personal", args.parent_folder)

    # 2. Create Book Tracking spreadsheet
    print("\n[2/3] Creating 'Book Tracking' spreadsheet...")
    sheet_id = create_spreadsheet(drive, sheets_svc, "Book Tracking", personal_folder_id)

    # 3. Set up headers
    print("\n[3/3] Setting up columns...")
    setup_headers(sheets_svc, sheet_id)

    # Seed first book if requested
    if args.seed:
        print("\n[SEED] Adding first book...")
        add_seed_book(sheets_svc, sheet_id)

    print(f"\n{'='*50}")
    print("BOOK TRACKING SETUP COMPLETE")
    print(f"Folder: Personal (in Claude Code Workspace)")
    print(f"Spreadsheet: Book Tracking")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
