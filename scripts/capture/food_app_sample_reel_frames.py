#!/usr/bin/env python3
"""Sample food-relevant candidate frames from vetted recipe Reels.

Produces three frames (early/middle/final) per Reel plus a contact sheet for manual
quality selection. The exact source URLs are the same 16 recipes that passed QA.
"""

from __future__ import annotations

import io
import json
import os
import pathlib
import subprocess
import tempfile

import requests
from PIL import Image, ImageDraw, ImageOps

APIFY_KEY = os.getenv("APIFY_API_KEY", "").strip()
ACTOR_URL = "https://api.apify.com/v2/acts/apify~instagram-reel-scraper/run-sync-get-dataset-items"
OUT = pathlib.Path("food-app-frame-candidates")
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "no-dough-chicken-coxinha": "https://www.instagram.com/reel/DbGI5b4sgtG/",
    "bread-scrap-pizza": "https://www.instagram.com/reel/DanabPmxvQt/",
    "easy-chicken-esfiha-style-foldover": "https://www.instagram.com/reel/DTLwkl9iQ6o/",
    "banana-neapolitan-nice-cream": "https://www.instagram.com/reel/DOovBtqCfHf/",
    "crispy-air-fryer-chicken-with-lemon-garlic-sauce": "https://www.instagram.com/reel/DNY-hv_JCbv/",
    "lighter-cheddar-mcmelt-style-burger": "https://www.instagram.com/reel/DLs0QdeJzJX/",
    "ginger-soy-chicken-marinade": "https://www.instagram.com/reel/DFbJXJHyLqB/",
    "zucchini-pancakes-with-beef-vegetable-filling": "https://www.instagram.com/reel/DYk8C2lJT9Z/",
    "airy-milk-powder-protein-dessert": "https://www.instagram.com/reel/Da0XA9Uusxu/",
    "moist-chocolate-oat-cake-with-cocoa-syrup": "https://www.instagram.com/reel/DQfXk12Ev89/",
    "one-pot-chuck-roast-with-vegetables": "https://www.instagram.com/reel/DZFzLEyRhCI/",
    "caramelized-onion-sun-dried-tomato-pasta": "https://www.instagram.com/reel/DaTJDDixdkJ/",
    "strawberry-protein-mousse": "https://www.instagram.com/reel/DbBHS1Ghm0M/",
    "street-corn-sweet-potato-beef-bowls": "https://www.instagram.com/reel/DadGpdwq5od/",
    "creamy-beef-cassava-vegetable-soup": "https://www.instagram.com/reel/DYZxG09RxdI/",
    "cheddar-onion-beef-flatbread": "https://www.instagram.com/reel/DYkDSqtgcL4/",
}

RATIOS = (0.12, 0.55, 0.90)


def shortcode(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def scrape() -> list[dict]:
    if not APIFY_KEY:
        raise RuntimeError("APIFY_API_KEY missing")
    response = requests.post(
        ACTOR_URL,
        params={"token": APIFY_KEY},
        json={"username": list(SOURCES.values()), "resultsLimit": 1, "includeTranscript": False},
        timeout=480,
    )
    response.raise_for_status()
    return response.json()


def download_video(url: str, path: pathlib.Path) -> None:
    with requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=120, stream=True) as response:
        response.raise_for_status()
        with path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)


def duration(path: pathlib.Path) -> float:
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        check=True, capture_output=True, text=True,
    )
    return float(proc.stdout.strip())


def extract(path: pathlib.Path, seconds: float, destination: pathlib.Path) -> None:
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{seconds:.3f}", "-i", str(path), "-frames:v", "1", "-q:v", "2", str(destination)],
        check=True,
    )


def make_contact(entries: list[dict]) -> None:
    cell_w, cell_h, label_h = 300, 300, 42
    cols = 3
    rows = len(entries)
    sheet = Image.new("RGB", (cols * cell_w, rows * (cell_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for row_idx, entry in enumerate(entries):
        slug = entry["slug"]
        for col_idx, frame_path in enumerate(entry.get("frames", [])):
            image = Image.open(frame_path).convert("RGB")
            image = ImageOps.fit(image, (cell_w, cell_h), method=Image.Resampling.LANCZOS)
            x, y = col_idx * cell_w, row_idx * (cell_h + label_h)
            sheet.paste(image, (x, y))
            label = f"{slug}  {['12%','55%','90%'][col_idx]}"
            draw.text((x + 5, y + cell_h + 5), label, fill="black")
    sheet.save(OUT / "contact-sheet.jpg", "JPEG", quality=88, optimize=True)


def main() -> int:
    items = scrape()
    by_code = {item.get("shortCode") or shortcode(item.get("inputUrl", "")): item for item in items}
    entries, failures = [], []
    with tempfile.TemporaryDirectory(prefix="food-app-reels-") as tmp:
        tmpdir = pathlib.Path(tmp)
        for slug, source in SOURCES.items():
            item = by_code.get(shortcode(source), {})
            video_url = item.get("videoUrl", "")
            if not video_url:
                failures.append({"slug": slug, "reason": "no videoUrl"})
                continue
            try:
                video = tmpdir / f"{slug}.mp4"
                download_video(video_url, video)
                total = duration(video)
                frame_paths = []
                for index, ratio in enumerate(RATIOS):
                    frame = OUT / f"{slug}__{index}.jpg"
                    extract(video, max(0.1, total * ratio), frame)
                    frame_paths.append(frame.as_posix())
                entries.append({"slug": slug, "creator": item.get("ownerUsername", ""), "duration": total, "frames": frame_paths})
                print(f"[frames] {slug}: duration={total:.1f}s")
            except Exception as exc:
                failures.append({"slug": slug, "reason": str(exc)})
                print(f"[frames] FAILED {slug}: {exc}")
    make_contact(entries)
    (OUT / "manifest.json").write_text(json.dumps({"entries": entries, "failures": failures}, indent=2), encoding="utf-8")
    print(f"[frames] recipes={len(entries)} failed={len(failures)}")
    return 0 if entries else 1


if __name__ == "__main__":
    raise SystemExit(main())
