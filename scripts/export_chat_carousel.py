#!/usr/bin/env python3
"""
export_chat_carousel.py — Screenshot each slide of an HTML carousel at 1080x1350px
Saves 6 PNGs to the Drive "Ready to Post" folder.

Usage:
  python export_chat_carousel.py --file CAROUSEL_1_6months_light.html
  python export_chat_carousel.py --drive-id 1FI-cCsPrDL4PXrnUcyoVY6t8JtrzqLdF
  python export_chat_carousel.py --all  # process all HTMLs in Ready to Post

Requirements:
  pip install playwright google-auth google-api-python-client
  playwright install chromium
"""
import os, sys, json, io, argparse, tempfile
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

READY_TO_POST_FOLDER = '1V_dpNy7EbEuEAa_iG2Yj873rYsJy6-DJ'
SLIDE_WIDTH  = 1080
SLIDE_HEIGHT = 1350  # 4:5 ratio for Instagram
SLIDE_COUNT  = 6
CREDS_PATH   = os.path.expanduser('~/ClaudeWorkspace/Credentials/sheets_token.json')


def get_drive():
    creds = Credentials.from_authorized_user_file(CREDS_PATH)
    return build('drive', 'v3', credentials=creds)


def download_html(drive, file_id):
    """Download an HTML file from Drive by ID."""
    content = drive.files().get_media(fileId=file_id, supportsAllDrives=True).execute()
    return content.decode('utf-8')


def list_html_files(drive):
    """List all HTML files in Ready to Post folder."""
    results = drive.files().list(
        q=f"'{READY_TO_POST_FOLDER}' in parents and mimeType='text/html' and trashed=false",
        fields="files(id,name)", supportsAllDrives=True, includeItemsFromAllDrives=True
    ).execute()
    return results.get('files', [])


def screenshot_carousel(html_content, output_dir, base_name):
    """Use Playwright to screenshot each slide. Returns list of PNG paths."""
    from playwright.sync_api import sync_playwright

    png_paths = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': SLIDE_WIDTH, 'height': SLIDE_HEIGHT})

        # Write HTML to temp file
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as f:
            f.write(html_content)
            tmp_path = f.name

        page.goto(f'file://{tmp_path}')
        page.wait_for_load_state('networkidle')

        for i in range(SLIDE_COUNT):
            if i > 0:
                # Click next button or trigger JS
                page.evaluate(f'go({i})')
                page.wait_for_timeout(500)  # wait for transition

            out_path = os.path.join(output_dir, f'{base_name}_slide{i+1:02d}.png')
            page.screenshot(path=out_path, clip={
                'x': 0, 'y': 0,
                'width': SLIDE_WIDTH,
                'height': SLIDE_HEIGHT
            })
            png_paths.append(out_path)
            print(f'  Screenshot: slide {i+1} → {os.path.basename(out_path)}')

        browser.close()
        os.unlink(tmp_path)

    return png_paths


def upload_pngs(drive, png_paths, carousel_name):
    """Upload PNGs to a subfolder in Ready to Post."""
    # Create subfolder named after carousel
    folder_name = f'PNG_{carousel_name}'
    existing = drive.files().list(
        q=f"name='{folder_name}' and '{READY_TO_POST_FOLDER}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id)", supportsAllDrives=True, includeItemsFromAllDrives=True
    ).execute()

    if existing.get('files'):
        folder_id = existing['files'][0]['id']
    else:
        folder = drive.files().create(
            body={'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [READY_TO_POST_FOLDER]},
            supportsAllDrives=True, fields='id'
        ).execute()
        folder_id = folder['id']

    uploaded = []
    for png_path in png_paths:
        fname = os.path.basename(png_path)
        with open(png_path, 'rb') as f:
            media = MediaIoBaseUpload(io.BytesIO(f.read()), mimetype='image/png')
        result = drive.files().create(
            body={'name': fname, 'parents': [folder_id]},
            media_body=media, supportsAllDrives=True, fields='id,name'
        ).execute()
        uploaded.append(result['name'])
        print(f'  Uploaded: {result["name"]}')

    print(f'All {len(uploaded)} PNGs → Drive folder: PNG_{carousel_name}')
    return folder_id


def process_file(drive, file_id, file_name):
    base_name = Path(file_name).stem
    print(f'\nProcessing: {file_name}')

    html = download_html(drive, file_id)

    with tempfile.TemporaryDirectory() as tmpdir:
        png_paths = screenshot_carousel(html, tmpdir, base_name)
        if png_paths:
            folder_id = upload_pngs(drive, png_paths, base_name)
            print(f'Done: {base_name} → {len(png_paths)} PNGs in Drive')
        else:
            print(f'ERROR: No screenshots captured for {file_name}')


def main():
    parser = argparse.ArgumentParser(description='Export carousel HTML slides to PNGs')
    parser.add_argument('--file', help='Local HTML file path')
    parser.add_argument('--drive-id', help='Drive file ID of HTML carousel')
    parser.add_argument('--all', action='store_true', help='Process all HTML files in Ready to Post folder')
    args = parser.parse_args()

    drive = get_drive()

    if args.all:
        files = list_html_files(drive)
        if not files:
            print('No HTML files found in Ready to Post folder.')
            return
        for f in files:
            process_file(drive, f['id'], f['name'])

    elif args.drive_id:
        meta = drive.files().get(fileId=args.drive_id, fields='name', supportsAllDrives=True).execute()
        process_file(drive, args.drive_id, meta['name'])

    elif args.file:
        with open(args.file, 'r') as f:
            html = f.read()
        base_name = Path(args.file).stem
        with tempfile.TemporaryDirectory() as tmpdir:
            png_paths = screenshot_carousel(html, tmpdir, base_name)
            if png_paths:
                upload_pngs(drive, png_paths, base_name)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
