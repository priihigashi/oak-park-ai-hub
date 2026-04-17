#!/usr/bin/env python3
"""
generate_image_openai.py
========================
Standalone OpenAI image generator.

Supports:
  - dall-e-3  → URL response → download → upload to Drive
  - gpt-image-1 → b64_json response → decode → upload to Drive

Usage:
  python scripts/generate_image_openai.py \
    --prompt "modern kitchen renovation, luxury style" \
    --model dall-e-3 \
    --size 1024x1792 \
    --drive_folder_id 1um7y2Yt8zi9KGxev6kfFJYgrkMYwrCNh \
    --filename "kitchen_concept_001"

Env vars required:
  OPENAI_API_KEY  — OpenAI API key
  SHEETS_TOKEN    — Google OAuth refresh token JSON (for Drive upload)

Drive upload uses supportsAllDrives=True — works with any shared drive folder.
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
SHEETS_TOKEN   = os.environ.get("SHEETS_TOKEN", "")

VALID_MODELS = {"dall-e-3", "gpt-image-1"}
VALID_SIZES_DALLE3 = {"1024x1024", "1792x1024", "1024x1792"}
VALID_SIZES_GPT    = {"1024x1024", "1536x1024", "1024x1536", "auto"}


def _get_drive_token() -> str:
    td = json.loads(SHEETS_TOKEN)
    data = urllib.parse.urlencode({
        "client_id":     td["client_id"],
        "client_secret": td["client_secret"],
        "refresh_token": td["refresh_token"],
        "grant_type":    "refresh_token",
    }).encode()
    resp = json.loads(urllib.request.urlopen(
        urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    ).read())
    return resp["access_token"]


def _generate_dalle3(prompt: str, size: str, quality: str) -> bytes:
    """Returns raw image bytes from dall-e-3 URL response."""
    size = size if size in VALID_SIZES_DALLE3 else "1024x1024"
    payload = json.dumps({
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality,
        "response_format": "url",
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
    url = resp["data"][0]["url"]
    revised = resp["data"][0].get("revised_prompt", "")
    if revised:
        print(f"  Revised prompt: {revised[:100]}...")
    print(f"  Image URL: {url[:80]}...")
    return urllib.request.urlopen(url, timeout=60).read()


def _generate_gpt_image1(prompt: str, size: str, quality: str) -> bytes:
    """Returns raw image bytes from gpt-image-1 b64_json response."""
    size = size if size in VALID_SIZES_GPT else "1024x1024"
    payload = json.dumps({
        "model": "gpt-image-1",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=180).read())
    b64 = resp["data"][0]["b64_json"]
    return base64.b64decode(b64)


def _upload_to_drive(image_bytes: bytes, filename: str, folder_id: str, mimetype: str = "image/png") -> dict:
    """Upload bytes to Google Drive shared folder. Returns {id, name, webViewLink}."""
    token = _get_drive_token()

    boundary = b"----OakParkOpenAIBoundary"
    metadata = json.dumps({"name": filename, "parents": [folder_id]}).encode()
    body = (
        b"--" + boundary + b"\r\n"
        b"Content-Type: application/json; charset=UTF-8\r\n\r\n"
        + metadata + b"\r\n"
        b"--" + boundary + b"\r\n"
        + f"Content-Type: {mimetype}\r\n\r\n".encode()
        + image_bytes + b"\r\n"
        b"--" + boundary + b"--\r\n"
    )
    req = urllib.request.Request(
        "https://www.googleapis.com/upload/drive/v3/files"
        "?uploadType=multipart&supportsAllDrives=true&fields=id,name,webViewLink",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/related; boundary={boundary.decode()}",
        },
    )
    result = json.loads(urllib.request.urlopen(req, timeout=120).read())
    return result


def main():
    parser = argparse.ArgumentParser(description="Generate image via OpenAI and upload to Drive")
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--model", default="dall-e-3", choices=list(VALID_MODELS))
    parser.add_argument("--size", default="1024x1024", help="Image size (e.g. 1024x1792)")
    parser.add_argument("--quality", default="standard", choices=["standard", "hd", "high", "medium", "low"])
    parser.add_argument("--drive_folder_id", default="", help="Drive folder ID to upload into")
    parser.add_argument("--filename", default="openai_generated", help="Output filename (no extension)")
    parser.add_argument("--local_out", default="", help="Also save locally to this path")
    args = parser.parse_args()

    if not OPENAI_API_KEY:
        sys.exit("ERROR: OPENAI_API_KEY not set")

    print(f"[openai-image] model={args.model} size={args.size} quality={args.quality}")
    print(f"[openai-image] prompt: {args.prompt[:100]}...")

    # Generate
    if args.model == "dall-e-3":
        image_bytes = _generate_dalle3(args.prompt, args.size, args.quality)
        ext = "png"
        mimetype = "image/png"
    else:
        image_bytes = _generate_gpt_image1(args.prompt, args.size, args.quality)
        ext = "png"
        mimetype = "image/png"

    print(f"  Generated {len(image_bytes):,} bytes")
    filename = f"{args.filename}.{ext}"

    # Optional local save
    if args.local_out:
        Path(args.local_out).write_bytes(image_bytes)
        print(f"  Saved locally: {args.local_out}")

    # Drive upload
    if args.drive_folder_id and SHEETS_TOKEN:
        print(f"[openai-image] Uploading to Drive folder {args.drive_folder_id}...")
        result = _upload_to_drive(image_bytes, filename, args.drive_folder_id, mimetype)
        file_id   = result.get("id", "")
        file_link = result.get("webViewLink", "")
        print(f"  Drive file: {result.get('name')}")
        print(f"  Drive link: {file_link}")
        print(f"DRIVE_FILE_ID={file_id}")
        print(f"DRIVE_LINK={file_link}")
    elif not args.drive_folder_id:
        print("[openai-image] No drive_folder_id — skipping upload")

    print(f"[openai-image] Done — {filename}")


if __name__ == "__main__":
    main()
