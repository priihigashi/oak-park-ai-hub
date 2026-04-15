#!/usr/bin/env python3
"""
Render 5 FORMAT-005 slides via Replicate (Ideogram 3 or Recraft V3) and upload to Drive.
Called from .github/workflows/carousel_compare.yml.
"""
import os, sys, json, time, base64, io
from pathlib import Path

TOOL    = os.environ["TOOL"]     # ideogram | recraft
PALETTE = os.environ["PALETTE"]  # dark | light

HERE = Path(__file__).parent
cfg  = json.loads((HERE / "prompts.json").read_text())
desc    = cfg[PALETTE]["desc"]
slides  = cfg[PALETTE]["slides"]
folder  = cfg["folders"]["Ideogram" if TOOL == "ideogram" else "Recraft"]

import requests

REPLICATE_TOKEN = os.environ["REPLICATE_API_TOKEN"]

MODELS = {
    "ideogram": "ideogram-ai/ideogram-v3-quality",
    "recraft":  "recraft-ai/recraft-v3",
}
MODEL = MODELS[TOOL]


def run_replicate(prompt: str) -> bytes:
    """Run a Replicate model synchronously; return PNG bytes."""
    if TOOL == "ideogram":
        payload = {
            "input": {
                "prompt": prompt,
                "aspect_ratio": "3:4",
                "resolution": "None",
                "magic_prompt_option": "Off",
                "style_type": "None",
            }
        }
    else:  # recraft
        payload = {
            "input": {
                "prompt": prompt,
                "size": "1024x1365",
                "style": "digital_illustration",
            }
        }

    # Retry on 429 rate limits with exponential backoff
    for attempt in range(6):
        r = requests.post(
            f"https://api.replicate.com/v1/models/{MODEL}/predictions",
            headers={
                "Authorization": f"Bearer {REPLICATE_TOKEN}",
                "Content-Type": "application/json",
                "Prefer": "wait=60",
            },
            json=payload,
            timeout=120,
        )
        if r.status_code == 429:
            wait = 10 * (2 ** attempt)
            print(f"  429 rate-limited, sleeping {wait}s (attempt {attempt+1}/6)", flush=True)
            time.sleep(wait)
            continue
        r.raise_for_status()
        break
    else:
        raise RuntimeError("Replicate 429 after 6 retries")
    data = r.json()

    # Poll until succeeded
    status = data.get("status")
    get_url = data.get("urls", {}).get("get")
    while status in ("starting", "processing"):
        time.sleep(3)
        pr = requests.get(get_url, headers={"Authorization": f"Bearer {REPLICATE_TOKEN}"})
        data = pr.json()
        status = data.get("status")

    if status != "succeeded":
        raise RuntimeError(f"Replicate status={status}: {data.get('error')}")

    output = data["output"]
    url = output[0] if isinstance(output, list) else output
    img = requests.get(url, timeout=120)
    img.raise_for_status()
    return img.content


# --- Upload to Drive ---
from google.oauth2.service_account import Credentials as SACreds
from google.oauth2.credentials import Credentials as OAuthCreds
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

# Workflow provides OAuth token file (matches avatar_generate pattern)
sheets_token = os.environ.get("SHEETS_TOKEN_JSON")
if sheets_token:
    Path("/tmp/sheets_token.json").write_text(sheets_token)
    creds = OAuthCreds.from_authorized_user_file("/tmp/sheets_token.json")
else:
    raise RuntimeError("SHEETS_TOKEN_JSON env var required")

drive = build("drive", "v3", credentials=creds)


def upload(name: str, content: bytes):
    media = MediaInMemoryUpload(content, mimetype="image/png", resumable=False)
    f = drive.files().create(
        body={"name": name, "parents": [folder]},
        media_body=media,
        supportsAllDrives=True,
        fields="id,name",
    ).execute()
    print(f"  uploaded {f['name']} ({f['id']})", flush=True)


for i, slide in enumerate(slides, 1):
    prompt = desc + " " + slide
    name = f"{TOOL}_{PALETTE}_s{i}.png"
    print(f"[{time.strftime('%H:%M:%S')}] {name} ...", flush=True)
    try:
        img = run_replicate(prompt)
        upload(name, img)
    except Exception as e:
        print(f"  FAIL {name}: {e}", flush=True)
    time.sleep(12)

print(f"{TOOL}-{PALETTE} done.", flush=True)
