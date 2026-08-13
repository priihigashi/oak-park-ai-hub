#!/usr/bin/env python3
"""Food App recipe ingestion for Instagram captures."""

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
MAX_RECIPES = int(os.getenv("FOOD_APP_MAX_RECIPES", "0") or "0")
METADATA_BATCH_SIZE = int(os.getenv("FOOD_APP_METADATA_BATCH_SIZE", "5") or "5")

RECIPE_MARKERS = (
    "project: food app", "category: food app", "category: recipe", "category: recipes",
    "recipe capture", "recipe reel", "recipe app", "recipe collection", "food capture",
    "beans recipe capture", "cheat day",
)

INGEST_HEADERS = [
    "QUEUE ROW", "SOURCE URL", "CREATOR", "RECIPE EN", "RECIPE PT", "CATEGORY",
    "DIET LABEL", "STATUS", "USED AUDIO", "CAPTION CHARS", "TRANSCRIPT CHARS",
    "INGREDIENTS EN JSON", "INGREDIENTS PT JSON", "STEPS EN JSON", "STEPS PT JSON",
    "NUTRITION ASSESSMENT", "SUBSTITUTIONS JSON", "LIGHTER SWAPS JSON", "EQUIPMENT JSON",
    "IMAGE PROMPT", "SOURCE CAPTION", "TRANSCRIPT", "UNCERTAINTIES JSON", "FULL RECIPE JSON",
    "UPDATED AT",
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


def _start_apify_chunk(urls: list[str]) -> tuple[str, list[str]]:
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
    return resp.json()["data"]["id"], direct


def _wait_apify_run(run_id: str) -> str:
    status = "RUNNING"
    for _ in range(18):
        time.sleep(10)
        response = requests.get(
            f"{APIFY_BASE}/actor-runs/{run_id}",
            params={"token": APIFY_KEY}, timeout=20,
        )
        response.raise_for_status()
        status = response.json()["data"]["status"]
        if status in {"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"}:
            break
    return status


def _read_apify_items(run_id: str, limit: int) -> dict[str, dict[str, Any]]:
    by_code: dict[str, dict[str, Any]] = {}
    items = requests.get(
        f"{APIFY_BASE}/actor-runs/{run_id}/dataset/items",
        params={"token": APIFY_KEY, "format": "json", "limit": limit}, timeout=45,
    ).json()
    for item in items:
        md = _metadata_from_item(item)
        code = md["short_code"] or shortcode(md["raw_url"])
        if code:
            by_code[code] = md
    return by_code


def _abort_apify_run(run_id: str) -> None:
    if not run_id:
        return
    try:
        requests.post(
            f"{APIFY_BASE}/actor-runs/{run_id}/abort",
            params={"token": APIFY_KEY}, timeout=20,
        )
    except Exception:
        pass


def _fetch_apify_chunk(urls: list[str]) -> dict[str, dict[str, Any]]:
    if not APIFY_KEY or not urls:
        return {}
    run_id = ""
    try:
        run_id, direct = _start_apify_chunk(urls)
        status = _wait_apify_run(run_id)
        by_code = _read_apify_items(run_id, len(direct) + 10)
        if status not in {"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"}:
            _abort_apify_run(run_id)
        return by_code
    except Exception as exc:
        print(f"[food-app] Apify chunk failed: {exc}; using concurrent fallback")
        _abort_apify_run(run_id)
        return {}


def _fetch_one_metadata(url: str) -> tuple[str, dict[str, Any]]:
    try:
        return url, cp.fetch_reel_metadata(url) or {}
    except Exception as exc:
        print(f"[food-app] metadata fallback failed for {shortcode(url)}: {exc}")
        return url, {}


def _fill_metadata_fallbacks(urls: list[str], by_code: dict[str, dict[str, Any]]) -> None:
    missing = [u for u in urls if shortcode(u) not in by_code]
    if not missing:
        return
    with ThreadPoolExecutor(max_workers=min(4, len(missing))) as pool:
        futures = [pool.submit(_fetch_one_metadata, u) for u in missing]
        for future in as_completed(futures):
            url, md = future.result()
            by_code[shortcode(url)] = md


def fetch_metadata_batch(urls: list[str]) -> dict[str, dict[str, Any]]:
    by_code = _fetch_apify_chunk(urls)
    _fill_metadata_fallbacks(urls, by_code)
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
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError("LLM returned no JSON object")
    return json.loads(match.group(0))


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
- needs_audio=true if the caption alone does not provide enough exact information for a usable recipe,
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
    sheet = gc.open_by_key(FOOD_TRACKER_ID)
    try:
        ws = sheet.worksheet(INGEST_TAB)
    except Exception:
        ws = sheet.add_worksheet(title=INGEST_TAB, rows=500, cols=len(INGEST_HEADERS))
        ws.append_row(INGEST_HEADERS, value_input_option="RAW")
        ws.freeze(rows=1)
    headers = ws.row_values(1)
    if headers != INGEST_HEADERS:
        ws.update("A1", [INGEST_HEADERS], value_input_option="RAW")
    return ws


def _recipe_record(queue_row: int, url: str, metadata: dict[str, Any], recipe: dict[str, Any], transcript: str, status: str) -> list[Any]:
    creator = metadata.get("creator_handle", "") or metadata.get("creator_name", "")
    return [
        queue_row, url, creator, recipe.get("title_en", ""), recipe.get("title_pt", ""),
        recipe.get("primary_category", ""), recipe.get("diet_label", ""), status,
        "YES" if transcript else "NO", len(metadata.get("caption", "") or ""), len(transcript or ""),
        json.dumps(recipe.get("ingredients_en", []), ensure_ascii=False),
        json.dumps(recipe.get("ingredients_pt", []), ensure_ascii=False),
        json.dumps(recipe.get("steps_en", []), ensure_ascii=False),
        json.dumps(recipe.get("steps_pt", []), ensure_ascii=False), recipe.get("nutrition_assessment", ""),
        json.dumps(recipe.get("substitutions", []), ensure_ascii=False),
        json.dumps(recipe.get("lighter_swaps", []), ensure_ascii=False),
        json.dumps(recipe.get("equipment", []), ensure_ascii=False), recipe.get("image_prompt", ""),
        metadata.get("caption", "") or "", transcript or "",
        json.dumps(recipe.get("uncertainties", []), ensure_ascii=False),
        json.dumps(recipe, ensure_ascii=False), now_iso(),
    ]


def upsert_ingest(ws, ingest_index: dict[str, int], queue_row: int, url: str, metadata: dict[str, Any], recipe: dict[str, Any], transcript: str) -> str:
    status = "NEEDS REVIEW" if recipe.get("needs_human_review") or recipe.get("uncertainties") else "READY TO IMPORT"
    record = _recipe_record(queue_row, url, metadata, recipe, transcript, status)
    target_row = ingest_index.get(str(queue_row))
    if target_row:
        ws.update(f"A{target_row}:Y{target_row}", [record], value_input_option="RAW")
    else:
        ws.append_row(record, value_input_option="RAW")
        ingest_index[str(queue_row)] = len(ingest_index) + 2
    return status


def update_queue_row(queue_ws, queue_row: int, success: bool, status: str = "", error: str = "") -> None:
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


def _collect_candidates(queue_ws) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for sheet_row, row in enumerate(queue_ws.get_all_values()[1:], start=2):
        padded = row + [""] * (16 - len(row))
        url, note = padded[1].strip(), padded[2].strip()
        if not url or "instagram.com/" not in url:
            continue
        if not is_recipe_row(note, padded[7].strip()):
            continue
        if padded[3].strip().upper() == "TRUE" and not padded[5].strip().lower().startswith("food app"):
            continue
        candidates.append({"row": sheet_row, "url": url, "note": note})
    return candidates


def _build_recipe(cand: dict[str, Any], metadata: dict[str, Any]) -> tuple[dict[str, Any], str]:
    url, note = cand["url"], cand["note"]
    prelim = run_llm(note, url, metadata, transcript="")
    transcript = transcribe_if_needed(url, metadata, prelim)
    recipe = run_llm(note, url, metadata, transcript=transcript) if transcript else prelim
    if prelim.get("needs_audio") and not transcript:
        recipe.setdefault("uncertainties", []).append(
            "Audio/visual details were requested but transcription was unavailable; verify against the reel before final publication."
        )
        recipe["needs_human_review"] = True
        recipe["confidence"] = "low" if not metadata.get("caption") else recipe.get("confidence", "medium")
    validation = validate_recipe(recipe)
    if validation:
        recipe.setdefault("uncertainties", []).extend(validation)
        recipe["needs_human_review"] = True
    recipe["source"] = {
        "queue_row": cand["row"], "url": url,
        "creator_handle": metadata.get("creator_handle", ""),
        "creator_name": metadata.get("creator_name", ""),
        "caption": metadata.get("caption", ""), "transcript": transcript,
        "capture_note": note,
    }
    return recipe, transcript


def _stage_candidate(queue_ws, ingest_ws, ingest_index, cand, metadata, summary, n, total) -> None:
    row_num, url = cand["row"], cand["url"]
    code = shortcode(url)
    print(f"\n[food-app] {n}/{total} row {row_num} {code}")
    try:
        recipe, transcript = _build_recipe(cand, metadata)
        (OUT_DIR / f"row_{row_num}_{code}.json").write_text(
            json.dumps(recipe, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        status = upsert_ingest(ingest_ws, ingest_index, row_num, url, metadata, recipe, transcript)
        update_queue_row(queue_ws, row_num, True, status=status)
        title = recipe.get("title_en") or recipe.get("title_pt")
        summary["success"].append({"row": row_num, "url": url, "title": title, "status": status})
        print(f"[food-app] staged: {title or code} [{status}]")
    except Exception as exc:
        update_queue_row(queue_ws, row_num, False, error=str(exc))
        summary["failed"].append({"row": row_num, "url": url, "error": str(exc)})
        print(f"[food-app] FAILED row {row_num}: {exc}")


def _process_chunks(queue_ws, ingest_ws, ingest_index, candidates, summary) -> None:
    total = len(candidates)
    for chunk_start in range(0, total, METADATA_BATCH_SIZE):
        chunk = candidates[chunk_start:chunk_start + METADATA_BATCH_SIZE]
        print(f"[food-app] metadata chunk {chunk_start + 1}-{chunk_start + len(chunk)} of {total}")
        metadata_map = fetch_metadata_batch([c["url"] for c in chunk])
        for offset, cand in enumerate(chunk, start=1):
            metadata = metadata_map.get(shortcode(cand["url"]), {}) or {}
            _stage_candidate(
                queue_ws, ingest_ws, ingest_index, cand, metadata, summary, chunk_start + offset, total
            )


def main() -> int:
    gc = cp.get_sheets_client()
    if not gc:
        raise RuntimeError("Google Sheets authentication unavailable")
    queue_ws = gc.open_by_key(IDEAS_INBOX_ID).worksheet(QUEUE_TAB)
    ingest_ws = ensure_ingest_sheet(gc)
    existing_ingest = ingest_ws.get_all_values()
    ingest_index = {
        str(row[0]).strip(): idx for idx, row in enumerate(existing_ingest[1:], start=2)
        if row and str(row[0]).strip()
    }
    candidates = _collect_candidates(queue_ws)
    if MAX_RECIPES > 0:
        candidates = candidates[:MAX_RECIPES]
    print(f"[food-app] recipe candidates: {len(candidates)}")
    if not candidates:
        return 0
    summary = {"started_at": now_iso(), "candidate_count": len(candidates), "success": [], "failed": []}
    _process_chunks(queue_ws, ingest_ws, ingest_index, candidates, summary)
    summary["finished_at"] = now_iso()
    (OUT_DIR / "batch_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n[food-app] done: {len(summary['success'])} staged, {len(summary['failed'])} failed")
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
