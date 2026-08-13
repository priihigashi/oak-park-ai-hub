#!/usr/bin/env python3
"""Food App recipe ingestion for Instagram captures.

Purpose
-------
Process recipe rows from the canonical ``📲 Capture Queue`` without sending them
through the generic News/OPC router. The job is deliberately caption-first:
Instagram caption metadata is scraped in one Apify batch, then audio is downloaded
and transcribed only when the caption is not sufficient to reconstruct a recipe.

Outputs
-------
* Structured bilingual recipe JSON under ``transcripts/food_app/`` (workflow artifact).
* Upserted rows in the existing ``Food APP — Tracker`` tab ``🍳 RECIPE INGESTION``.
* Capture Queue rows are explicitly routed to ``food app`` and marked captured only
  after a structured recipe record has been written. ``READY TO BUILD`` remains a
  separate gate for app import/review.

This script does NOT publish to the live priih.chatgpt.site deployments. Their
editable source is not present in Drive/GitHub; the structured records are the
portable import payload for the app once that source is available.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

# Reuse the production capture stack for Sheets auth, audio download,
# transcription provider fallback, and Claude→OpenAI text fallback.
import capture_pipeline as cp

IDEAS_INBOX_ID = os.getenv("IDEAS_INBOX_ID", "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU")
QUEUE_TAB = "📲 Capture Queue"
FOOD_TRACKER_ID = os.getenv("FOOD_TRACKER_ID", "1dMlteQF_SimvBJVAMDKhmgFaasiPn8Ki0HphcuppWQc")
INGEST_TAB = "🍳 RECIPE INGESTION"
TRACKER_URL = f"https://docs.google.com/spreadsheets/d/{FOOD_TRACKER_ID}/edit"
OUT_DIR = Path("transcripts/food_app")
OUT_DIR.mkdir(parents=True, exist_ok=True)
APIFY_BASE = "https://api.apify.com/v2"
APIFY_KEY = os.getenv("APIFY_API_KEY", "")
MAX_RECIPES = int(os.getenv("FOOD_APP_MAX_RECIPES", "0") or "0")  # 0 = all
METADATA_BATCH_SIZE = int(os.getenv("FOOD_APP_METADATA_BATCH_SIZE", "5") or "5")

RECIPE_MARKERS = (
    "project: food app",
    "category: food app",
    "category: recipe",
    "category: recipes",
    "recipe capture",
    "recipe reel",
    "recipe app",
    "recipe collection",
    "food capture",
    "beans recipe capture",
    "cheat day",
)

INGEST_HEADERS = [
    "QUEUE ROW", "SOURCE URL", "CREATOR", "RECIPE EN", "RECIPE PT",
    "CATEGORY", "DIET LABEL", "STATUS", "USED AUDIO", "CAPTION CHARS",
    "TRANSCRIPT CHARS", "INGREDIENTS EN JSON", "INGREDIENTS PT JSON",
    "STEPS EN JSON", "STEPS PT JSON", "NUTRITION ASSESSMENT",
    "SUBSTITUTIONS JSON", "LIGHTER SWAPS JSON", "EQUIPMENT JSON",
    "IMAGE PROMPT", "SOURCE CAPTION", "TRANSCRIPT", "UNCERTAINTIES JSON",
    "FULL RECIPE JSON", "UPDATED AT",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def norm_url(url: str) -> str:
    return url.strip().split("?")[0].rstrip("/")


def shortcode(url: str) -> str:
    m = re.search(r"instagram\.com/(?:reel|p)/([^/?#]+)", url)
    return m.group(1) if m else norm_url(url)


def is_recipe_row(comment: str, project: str) -> bool:
    c = (comment or "").lower()
    p = (project or "").strip().lower()
    if p == "food app":
        return True
    return any(marker in c for marker in RECIPE_MARKERS)


def _metadata_from_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "creator_handle": item.get("ownerUsername", "") or item.get("username", ""),
        "creator_name": item.get("ownerFullName", "") or item.get("fullName", ""),
        "caption": item.get("caption", "") or item.get("text", ""),
        "likes": item.get("likesCount", 0),
        "comments": item.get("commentsCount", 0),
        "views": item.get("videoViewCount", 0) or item.get("videoPlayCount", 0),
        "display_url": item.get("displayUrl", "") or item.get("imageUrl", ""),
        "short_code": item.get("shortCode", "") or item.get("shortcode", ""),
        "raw_url": item.get("url", "") or item.get("inputUrl", ""),
    }


def fetch_metadata_batch(urls: list[str]) -> dict[str, dict[str, Any]]:
    """Fetch Instagram captions/credits efficiently for a small chunk.

    Apify gets one batch run with a bounded three-minute wait. Any missing items
    then use the already-tested production helper concurrently instead of making
    the whole batch wait on 28 sequential actor runs.
    """
    by_code: dict[str, dict[str, Any]] = {}
    run_id = ""
    if APIFY_KEY and urls:
        try:
            direct = [norm_url(u) for u in urls]
            payload = {
                "directUrls": direct,
                "resultsLimit": len(direct),
                "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["DATACENTER"]},
            }
            resp = requests.post(
                f"{APIFY_BASE}/acts/apify~instagram-post-scraper/runs",
                params={"token": APIFY_KEY}, json=payload, timeout=30,
            )
            resp.raise_for_status()
            run_id = resp.json()["data"]["id"]
            status = "RUNNING"
            for _ in range(18):  # max ~3 minutes, matching production helper
                time.sleep(10)
                sr = requests.get(
                    f"{APIFY_BASE}/actor-runs/{run_id}",
                    params={"token": APIFY_KEY}, timeout=20,
                )
                sr.raise_for_status()
                status = sr.json()["data"]["status"]
                if status in {"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"}:
                    break
            # Read whatever the run produced even if it hit our local wait ceiling.
            items = requests.get(
                f"{APIFY_BASE}/actor-runs/{run_id}/dataset/items",
                params={"token": APIFY_KEY, "format": "json", "limit": len(direct) + 10},
                timeout=45,
            ).json()
            for item in items:
                md = _metadata_from_item(item)
                code = md["short_code"] or shortcode(md["raw_url"])
                if code:
                    by_code[code] = md
            if status not in {"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"}:
                # Stop a still-running actor before falling back so it does not keep burning units.
                try:
                    requests.post(
                        f"{APIFY_BASE}/actor-runs/{run_id}/abort",
                        params={"token": APIFY_KEY}, timeout=20,
                    )
                except Exception:
                    pass
        except Exception as exc:
            print(f"[food-app] Apify chunk failed: {exc}; using concurrent fallback")

    missing = [u for u in urls if shortcode(u) not in by_code]
    if missing:
        def _fallback(url: str):
            try:
                return url, cp.fetch_reel_metadata(url) or {}
            except Exception as exc:
                print(f"[food-app] metadata fallback failed for {shortcode(url)}: {exc}")
                return url, {}

        with ThreadPoolExecutor(max_workers=min(4, len(missing))) as pool:
            futures = [pool.submit(_fallback, u) for u in missing]
            for fut in as_completed(futures):
                url, md = fut.result()
                by_code[shortcode(url)] = md
    return by_code


def _extract_json(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        raise ValueError("LLM returned no JSON object")
    return json.loads(m.group(0))


def recipe_prompt(note: str, url: str, metadata: dict[str, Any], transcript: str = "") -> str:
    caption = metadata.get("caption", "") or ""
    return f"""You are extracting one recipe for Priscila's existing bilingual Food App.
Do not invent missing quantities, temperatures, times, yields, nutrition, or creator claims.
Caption is the preferred source when it contains the recipe. If the user note explicitly says
caption is canonical, preserve its quantities exactly and use transcript only for technique.
If caption and transcript conflict, record the conflict in uncertainties instead of silently choosing.

SOURCE URL: {url}
CREATOR HANDLE: {metadata.get('creator_handle','')}
CREATOR NAME: {metadata.get('creator_name','')}
USER CAPTURE NOTE:
{note}

INSTAGRAM CAPTION:
{caption}

AUDIO TRANSCRIPT (may be blank on first pass):
{transcript}

Return JSON ONLY with this exact top-level schema. Arrays may be empty only when source data is truly absent.
{{
  "needs_audio": true,
  "original_title": "",
  "title_en": "",
  "title_pt": "",
  "primary_category": "Breakfast|Lunch|Dinner|Snack|Dessert|Soup|Salad|Pasta|Brazilian|Marinade|BBQ|Other",
  "diet_label": "healthy|high-protein|balanced|fit|treat|cheat-day|comfort-food|regular|unclear",
  "tags": [],
  "equipment": [],
  "servings": null,
  "prep_minutes": null,
  "cook_minutes": null,
  "total_minutes": null,
  "ingredients_en": [{{"quantity":"","unit":"","ingredient":"","notes":""}}],
  "ingredients_pt": [{{"quantity":"","unit":"","ingredient":"","notes":""}}],
  "steps_en": [],
  "steps_pt": [],
  "storage_en": "",
  "storage_pt": "",
  "substitutions": [{{"original":"","us_substitute":"","brand_if_ambiguous":"","notes":""}}],
  "lighter_swaps": [{{"original":"","swap":"","impact_on_dish":""}}],
  "nutrition_assessment": "",
  "estimated_macros": {{"calories":null,"protein_g":null,"carbs_g":null,"fat_g":null,"fiber_g":null,"basis":""}},
  "allergens": [],
  "kid_notes": "",
  "claim_review": "",
  "potato_alternative": {{"included":false,"title_en":"","title_pt":"","ingredients_en":[],"ingredients_pt":[],"steps_en":[],"steps_pt":[],"technical_notes":""}},
  "image_prompt": "Photorealistic finished-dish food photograph prompt describing the actual recipe, plating, texture, toppings, and cuisine. No text, logos, people, or copied creator styling.",
  "uncertainties": [],
  "needs_human_review": false,
  "confidence": "high|medium|low"
}}

Rules:
- needs_audio=true if the CAPTION ALONE does not provide enough exact information for a usable recipe,
  or if the capture note requires spoken/visual details not present in caption. Once transcript is supplied,
  set needs_audio=false unless there is still source information unavailable.
- Translate naturally EN↔PT while preserving measurements. Add US-buyable substitutes for Brazilian-only items.
- Keep Portuguese original recipe names when culturally meaningful (e.g. coxinha, esfiha, requeijão).
- "Healthy"/"fit" claims must be evaluated, not copied. Body-shape claims must not be treated as established.
- For the mushroom recipe whose user note requests a potato alternative, develop the alternative carefully and
  explicitly explain moisture/binding/cooking adjustments; otherwise potato_alternative.included=false.
- If a pressure cooker is required, put it in equipment and flag it clearly in nutrition_assessment or uncertainties.
- Macros: only estimate when ingredient quantities and yield are sufficiently complete; otherwise leave null.
"""


def run_llm(note: str, url: str, metadata: dict[str, Any], transcript: str = "") -> dict[str, Any]:
    raw = cp._llm_text(recipe_prompt(note, url, metadata, transcript), max_tokens=7000)
    if not raw:
        raise RuntimeError("All text LLM providers failed")
    return _extract_json(raw)


def transcribe_if_needed(url: str, metadata: dict[str, Any], prelim: dict[str, Any]) -> str:
    if not prelim.get("needs_audio", True):
        return ""
    try:
        with tempfile.TemporaryDirectory(prefix="food-app-recipe-") as tmp:
            audio = cp.download_audio(url, tmp, metadata=metadata)
            if not audio or audio == "__ig_carousel__":
                return ""
            return cp.transcribe_audio(audio, url=url) or ""
    except Exception as exc:
        print(f"[food-app] audio/transcription failed for {shortcode(url)}: {exc}")
        return ""


def validate_recipe(recipe: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not (recipe.get("title_en") or recipe.get("title_pt") or recipe.get("original_title")):
        issues.append("missing recipe title")
    if not recipe.get("ingredients_en") and not recipe.get("ingredients_pt"):
        issues.append("missing ingredient list")
    if not recipe.get("steps_en") and not recipe.get("steps_pt"):
        issues.append("missing preparation steps")
    return issues


def ensure_ingest_sheet(gc):
    sh = gc.open_by_key(FOOD_TRACKER_ID)
    try:
        ws = sh.worksheet(INGEST_TAB)
    except Exception:
        ws = sh.add_worksheet(title=INGEST_TAB, rows=500, cols=len(INGEST_HEADERS))
        ws.append_row(INGEST_HEADERS, value_input_option="RAW")
        ws.freeze(rows=1)
    headers = ws.row_values(1)
    if headers != INGEST_HEADERS:
        ws.update("A1", [INGEST_HEADERS], value_input_option="RAW")
    return ws


def upsert_ingest(ws, ingest_index: dict[str, int], queue_row: int, url: str, metadata: dict[str, Any], recipe: dict[str, Any], transcript: str, used_audio: bool):
    creator = metadata.get("creator_handle", "") or metadata.get("creator_name", "")
    status = "NEEDS REVIEW" if recipe.get("needs_human_review") or recipe.get("uncertainties") else "READY TO IMPORT"
    record = [
        queue_row, url, creator, recipe.get("title_en", ""), recipe.get("title_pt", ""),
        recipe.get("primary_category", ""), recipe.get("diet_label", ""), status,
        "YES" if used_audio else "NO", len(metadata.get("caption", "") or ""), len(transcript or ""),
        json.dumps(recipe.get("ingredients_en", []), ensure_ascii=False),
        json.dumps(recipe.get("ingredients_pt", []), ensure_ascii=False),
        json.dumps(recipe.get("steps_en", []), ensure_ascii=False),
        json.dumps(recipe.get("steps_pt", []), ensure_ascii=False),
        recipe.get("nutrition_assessment", ""),
        json.dumps(recipe.get("substitutions", []), ensure_ascii=False),
        json.dumps(recipe.get("lighter_swaps", []), ensure_ascii=False),
        json.dumps(recipe.get("equipment", []), ensure_ascii=False),
        recipe.get("image_prompt", ""), metadata.get("caption", "") or "", transcript or "",
        json.dumps(recipe.get("uncertainties", []), ensure_ascii=False),
        json.dumps(recipe, ensure_ascii=False), now_iso(),
    ]
    target_row = ingest_index.get(str(queue_row))
    if target_row:
        ws.update(f"A{target_row}:Y{target_row}", [record], value_input_option="RAW")
    else:
        ws.append_row(record, value_input_option="RAW")
        ingest_index[str(queue_row)] = len(ingest_index) + 2
    return status


def update_queue_row(queue_ws, queue_row: int, success: bool, status: str = "", error: str = ""):
    # One batch request per row: preserves unrelated cells while preventing the
    # generic daily router from ever treating a recipe as News/OPC.
    updates = [{"range": f"H{queue_row}", "values": [["food app"]]}]
    if success:
        updates.extend([
            {"range": f"D{queue_row}", "values": [[True]]},
            {"range": f"F{queue_row}", "values": [["Food APP — recipe staged"]]},
            {"range": f"G{queue_row}", "values": [[TRACKER_URL]]},
            {"range": f"K{queue_row}", "values": [["Needs Review" if status == "NEEDS REVIEW" else "Ready to Import"]]},
        ])
    else:
        updates.extend([
            {"range": f"D{queue_row}", "values": [[False]]},
            {"range": f"F{queue_row}", "values": [["⚠️ Food recipe extraction failed"]]},
            {"range": f"G{queue_row}", "values": [[(error or "unknown error")[:400]]},
            {"range": f"K{queue_row}", "values": [["Needs Research"]]},
        ])
    queue_ws.batch_update(updates, value_input_option="USER_ENTERED")


def main() -> int:
    gc = cp.get_sheets_client()
    if not gc:
        raise RuntimeError("Google Sheets authentication unavailable")
    queue_ws = gc.open_by_key(IDEAS_INBOX_ID).worksheet(QUEUE_TAB)
    ingest_ws = ensure_ingest_sheet(gc)
    existing_ingest = ingest_ws.get_all_values()
    ingest_index = {str(r[0]).strip(): idx for idx, r in enumerate(existing_ingest[1:], start=2) if r and str(r[0]).strip()}

    rows = queue_ws.get_all_values()
    candidates: list[dict[str, Any]] = []
    for sheet_row, row in enumerate(rows[1:], start=2):
        padded = row + [""] * (16 - len(row))
        url = padded[1].strip()
        note = padded[2].strip()
        processed = padded[3].strip().upper()
        project = padded[7].strip()
        if not url or "instagram.com/" not in url:
            continue
        if not is_recipe_row(note, project):
            continue
        # If a recipe row was previously processed by another route, keep it out of this destructive pass.
        # Current Food App rows are pending; this guard avoids overwriting historical completed work.
        if processed == "TRUE" and not (padded[5].strip().lower().startswith("food app")):
            continue
        candidates.append({"row": sheet_row, "url": url, "note": note})

    if MAX_RECIPES > 0:
        candidates = candidates[:MAX_RECIPES]
    print(f"[food-app] recipe candidates: {len(candidates)}")
    if not candidates:
        return 0

    summary = {"started_at": now_iso(), "candidate_count": len(candidates), "success": [], "failed": []}

    for chunk_start in range(0, len(candidates), METADATA_BATCH_SIZE):
        chunk = candidates[chunk_start:chunk_start + METADATA_BATCH_SIZE]
        print(f"[food-app] metadata chunk {chunk_start + 1}-{chunk_start + len(chunk)} of {len(candidates)}")
        metadata_map = fetch_metadata_batch([c["url"] for c in chunk])

        for offset, cand in enumerate(chunk, start=1):
            n = chunk_start + offset
            row_num, url, note = cand["row"], cand["url"], cand["note"]
            code = shortcode(url)
            md = metadata_map.get(code, {}) or {}
            print(f"\n[food-app] {n}/{len(candidates)} row {row_num} {code}")
            try:
                prelim = run_llm(note, url, md, transcript="")
                transcript = transcribe_if_needed(url, md, prelim)
                recipe = run_llm(note, url, md, transcript=transcript) if transcript else prelim
                if prelim.get("needs_audio") and not transcript:
                    recipe.setdefault("uncertainties", []).append("Audio/visual details were requested but transcription was unavailable; verify against the reel before final publication.")
                    recipe["needs_human_review"] = True
                    recipe["confidence"] = "low" if not md.get("caption") else recipe.get("confidence", "medium")
                validation = validate_recipe(recipe)
                if validation:
                    recipe.setdefault("uncertainties", []).extend(validation)
                    recipe["needs_human_review"] = True
                recipe["source"] = {
                    "queue_row": row_num,
                    "url": url,
                    "creator_handle": md.get("creator_handle", ""),
                    "creator_name": md.get("creator_name", ""),
                    "caption": md.get("caption", ""),
                    "transcript": transcript,
                    "capture_note": note,
                }
                out_path = OUT_DIR / f"row_{row_num}_{code}.json"
                out_path.write_text(json.dumps(recipe, ensure_ascii=False, indent=2), encoding="utf-8")
                status = upsert_ingest(ingest_ws, ingest_index, row_num, url, md, recipe, transcript, bool(transcript))
                update_queue_row(queue_ws, row_num, True, status=status)
                summary["success"].append({"row": row_num, "url": url, "title": recipe.get("title_en") or recipe.get("title_pt"), "status": status})
                print(f"[food-app] staged: {recipe.get('title_en') or recipe.get('title_pt') or code} [{status}]")
            except Exception as exc:
                update_queue_row(queue_ws, row_num, False, error=str(exc))
                summary["failed"].append({"row": row_num, "url": url, "error": str(exc)})
                print(f"[food-app] FAILED row {row_num}: {exc}")

    summary["finished_at"] = now_iso()
    (OUT_DIR / "batch_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[food-app] done: {len(summary['success'])} staged, {len(summary['failed'])} failed")
    # Partial failures should surface as a failed workflow so they are not silently forgotten.
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
