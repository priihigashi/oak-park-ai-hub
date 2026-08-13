#!/usr/bin/env python3
"""Fetch source-accurate Instagram cover images for vetted Food App recipes.

The personal recipe site already uses source-derived imagery. This script keeps the
same personal-use posture: use Apify's official Instagram Reel Scraper on the exact
source URLs, download the reel cover/thumbnail, and normalize it to a 3:2 recipe-card
asset. It never publishes held/incomplete recipes.
"""

from __future__ import annotations

import io
import json
import os
import pathlib
import urllib.request

import requests
from PIL import Image, ImageFilter, ImageOps

APIFY_KEY = os.getenv("APIFY_API_KEY", "").strip()
ACTOR_URL = "https://api.apify.com/v2/acts/apify~instagram-reel-scraper/run-sync-get-dataset-items"
OUT = pathlib.Path("food-app-source-images")
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


def shortcode(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def scrape() -> list[dict]:
    if not APIFY_KEY:
        raise RuntimeError("APIFY_API_KEY missing")
    response = requests.post(
        ACTOR_URL,
        params={"token": APIFY_KEY},
        json={
            "username": list(SOURCES.values()),
            "resultsLimit": 1,
            "includeTranscript": False,
            "includeDownloadedVideo": False,
        },
        timeout=480,
    )
    response.raise_for_status()
    return response.json()


def pick_image_url(item: dict) -> str:
    for key in ("displayUrl", "imageUrl", "thumbnailUrl", "thumbnailSrc", "display_url"):
        value = item.get(key)
        if isinstance(value, str) and value.startswith("http"):
            return value
    images = item.get("images")
    if isinstance(images, list):
        for value in images:
            if isinstance(value, str) and value.startswith("http"):
                return value
            if isinstance(value, dict):
                for key in ("url", "src", "displayUrl"):
                    candidate = value.get(key)
                    if isinstance(candidate, str) and candidate.startswith("http"):
                        return candidate
    return ""


def download(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0", "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def normalize(raw: bytes, destination: pathlib.Path) -> None:
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    # Instagram covers are often portrait. Build a subtle blurred 3:2 canvas and
    # place the complete source cover in the middle so no food is cropped away.
    canvas_size = (1536, 1024)
    background = ImageOps.fit(image, canvas_size, method=Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(radius=30))
    background = Image.blend(background, Image.new("RGB", canvas_size, (20, 20, 20)), 0.18)
    foreground = image.copy()
    foreground.thumbnail((1536, 1024), Image.Resampling.LANCZOS)
    x = (canvas_size[0] - foreground.width) // 2
    y = (canvas_size[1] - foreground.height) // 2
    background.paste(foreground, (x, y))
    background.save(destination, "JPEG", quality=92, optimize=True, progressive=True)


def main() -> int:
    items = scrape()
    by_code = {}
    for item in items:
        code = item.get("shortCode") or shortcode(item.get("inputUrl", ""))
        if code:
            by_code[code] = item

    manifest = []
    failures = []
    for slug, source in SOURCES.items():
        code = shortcode(source)
        item = by_code.get(code, {})
        image_url = pick_image_url(item)
        if not image_url:
            failures.append({"slug": slug, "source": source, "reason": "no cover/thumbnail returned"})
            continue
        try:
            path = OUT / f"{slug}.jpg"
            normalize(download(image_url), path)
            manifest.append({
                "slug": slug,
                "source": source,
                "creator": item.get("ownerUsername", ""),
                "cover_source_url": image_url,
                "asset": path.as_posix(),
                "bytes": path.stat().st_size,
            })
            print(f"[image] {slug}: {path.stat().st_size} bytes")
        except Exception as exc:
            failures.append({"slug": slug, "source": source, "reason": str(exc)})

    (OUT / "manifest.json").write_text(
        json.dumps({"ready": manifest, "failures": failures}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[image] ready={len(manifest)} failed={len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
