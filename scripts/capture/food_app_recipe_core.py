"""Core helpers for Food App Instagram recipe ingestion.

The module reuses the existing capture stack for Instagram metadata, audio download,
transcription, Sheets auth, and LLM calls. Each helper intentionally stays small so
new recipe automation does not add complexity-gate debt.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import capture_pipeline as cp

IDEAS_INBOX_ID = os.getenv("IDEAS_INBOX_ID", "1IrFrCNGVIF7cvAr9cIuAXvCtUR_-eQN1mdCpHXpfbcU")
QUEUE_TAB = "📲 Capture Queue"
FOOD_TRACKER_ID = os.getenv("FOOD_TRACKER_ID", "1dMlteQF_SimvBJVAMDKhmgFaasiPn8Ki0HphcuppWQc")
INGEST_TAB = "🍳 RECIPE INGESTION"
TRACKER_URL = f"https://docs.google.com/spreadsheets/d/{FOOD_TRACKER_ID}/edit"
OUT_DIR = Path("transcripts/food_app")
OUT_DIR.mkdir(parents=True, exist_ok=True)
MAX_RECIPES = int(os.getenv("FOOD_APP_MAX_RECIPES", "0") or "0")
CHUNK_SIZE = int(os.getenv("FOOD_APP_METADATA_BATCH_SIZE", "5") or "5")

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
    "QUEUE ROW", "SOURCE URL", "CREATOR", "RECIPE EN", "RECIPE PT", "CATEGORY",
    "DIET LABEL", "STATUS", "USED AUDIO", "CAPTION CHARS", "TRANSCRIPT CHARS",
    "INGREDIENTS EN JSON", "INGREDIENTS PT JSON", "STEPS EN JSON", "STEPS PT JSON",
    "NUTRITION ASSESSMENT", "SUBSTITUTIONS JSON", "LIGHTER SWAPS JSON", "EQUIPMENT JSON",
    "IMAGE PROMPT", "SOURCE CAPTION", "TRANSCRIPT", "UNCERTAINTIES JSON", "FULL RECIPE JSON",
    "UPDATED AT",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def shortcode(url: str) -> str:
    match = re.search(r"instagram\.com/(?:reel|p)/([^/?#]+)", url)
    return match.group(1) if match else url.split("?")[0].rstrip("/")


def is_recipe_row(comment: str, project: str) -> bool:
    text = (comment or "").lower()
    return (project or "").strip().lower() == "food app" or any(marker in text for marker in RECIPE_MARKERS)


def collect_candidates(queue_ws) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for sheet_row, row in enumerate(queue_ws.get_all_values()[1:], start=2):
        padded = row + [""] * (16 - len(row))
        url, note = padded[1].strip(), padded[2].strip()
        if not url or "instagram.com/" not in url:
            continue
        if not is_recipe_row(note, padded[7]):
            continue
        if padded[3].strip().upper() == "TRUE" and not padded[5].strip().lower().startswith("food app"):
            continue
        candidates.append({"row": sheet_row, "url": url, "note": note})
    return candidates[:MAX_RECIPES] if MAX_RECIPES > 0 else candidates


def fetch_one_metadata(url: str) -> tuple[str, dict[str, Any]]:
    try:
        return url, cp.fetch_reel_metadata(url) or {}
    except Exception as exc:
        print(f"[food-app] metadata failed for {shortcode(url)}: {exc}")
        return url, {}


def fetch_metadata_chunk(urls: list[str]) -> dict[str, dict[str, Any]]:
    with ThreadPoolExecutor(max_workers=min(CHUNK_SIZE, len(urls))) as pool:
        pairs = list(pool.map(fetch_one_metadata, urls))
    return {shortcode(url): metadata for url, metadata in pairs}


def extract_json(text: str) -> dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip())
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
    if not match:
        raise ValueError("LLM returned no JSON object")
    return json.loads(match.group(0))


def recipe_prompt(note: str, url: str, metadata: dict[str, Any], transcript: str = "") -> str:
    return f"""Extract one recipe for Priscila's existing bilingual Food App.
Use only source-supported facts. Never invent missing quantities, temperatures, times,
yields, nutrition, or creator claims. Prefer the Instagram caption when it contains the
recipe. If the capture note says caption is canonical, preserve its quantities exactly.
If caption and transcript conflict, record the conflict in uncertainties.

SOURCE URL: {url}
CREATOR: {metadata.get('creator_handle','') or metadata.get('creator_name','')}
CAPTURE NOTE:\n{note}
INSTAGRAM CAPTION:\n{metadata.get('caption','') or ''}
AUDIO TRANSCRIPT:\n{transcript}

Return JSON ONLY with exactly this schema:
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
- needs_audio=true only when caption alone is insufficient or the capture note requires spoken details.
- Translate EN↔PT naturally while preserving measurements.
- Add US-buyable substitutes for Brazilian-only ingredients; preserve culturally meaningful names.
- Evaluate healthy/fit/body-shape claims instead of repeating them as facts.
- For the mushroom capture requesting a potato alternative, build the alternative and explain moisture/binding/cooking adjustments.
- Flag pressure-cooker requirements in equipment.
- Estimate macros only when quantities and yield are sufficiently complete; otherwise keep them null.
"""


def run_llm(note: str, url: str, metadata: dict[str, Any], transcript: str = "") -> dict[str, Any]:
    raw = cp._llm_text(recipe_prompt(note, url, metadata, transcript), max_tokens=7000)
    if not raw:
        raise RuntimeError("All text LLM providers failed")
    return extract_json(raw)


def transcribe_if_needed(url: str, metadata: dict[str, Any], recipe: dict[str, Any]) -> str:
    if not recipe.get("needs_audio", True):
        return ""
    try:
        with tempfile.TemporaryDirectory(prefix="food-app-recipe-") as tmp:
            audio = cp.download_audio(url, tmp, metadata=metadata)
            if not audio or audio == "__ig_carousel__":
                return ""
            return cp.transcribe_audio(audio, url=url) or ""
    except Exception as exc:
        print(f"[food-app] transcription failed for {shortcode(url)}: {exc}")
        return ""


def validation_issues(recipe: dict[str, Any]) -> list[str]:
    checks = (
        (bool(recipe.get("title_en") or recipe.get("title_pt") or recipe.get("original_title")), "missing recipe title"),
        (bool(recipe.get("ingredients_en") or recipe.get("ingredients_pt")), "missing ingredient list"),
        (bool(recipe.get("steps_en") or recipe.get("steps_pt")), "missing preparation steps"),
    )
    return [message for valid, message in checks if not valid]


def add_review_flags(recipe: dict[str, Any], metadata: dict[str, Any], prelim: dict[str, Any], transcript: str) -> None:
    if prelim.get("needs_audio") and not transcript:
        recipe.setdefault("uncertainties", []).append("Audio/visual details were needed but transcription was unavailable; verify against the reel.")
        recipe["needs_human_review"] = True
        recipe["confidence"] = "low" if not metadata.get("caption") else recipe.get("confidence", "medium")
    issues = validation_issues(recipe)
    if issues:
        recipe.setdefault("uncertainties", []).extend(issues)
        recipe["needs_human_review"] = True


def build_recipe(candidate: dict[str, Any], metadata: dict[str, Any]) -> tuple[dict[str, Any], str]:
    url, note = candidate["url"], candidate["note"]
    prelim = run_llm(note, url, metadata)
    transcript = transcribe_if_needed(url, metadata, prelim)
    recipe = run_llm(note, url, metadata, transcript) if transcript else prelim
    add_review_flags(recipe, metadata, prelim, transcript)
    recipe["source"] = {
        "queue_row": candidate["row"],
        "url": url,
        "creator_handle": metadata.get("creator_handle", ""),
        "creator_name": metadata.get("creator_name", ""),
        "caption": metadata.get("caption", ""),
        "transcript": transcript,
        "capture_note": note,
    }
    return recipe, transcript


def ensure_ingest_sheet(gc):
    spreadsheet = gc.open_by_key(FOOD_TRACKER_ID)
    try:
        ws = spreadsheet.worksheet(INGEST_TAB)
    except Exception:
        ws = spreadsheet.add_worksheet(title=INGEST_TAB, rows=500, cols=len(INGEST_HEADERS))
        ws.append_row(INGEST_HEADERS, value_input_option="RAW")
        ws.freeze(rows=1)
    if ws.row_values(1) != INGEST_HEADERS:
        ws.update("A1", [INGEST_HEADERS], value_input_option="RAW")
    return ws


def recipe_status(recipe: dict[str, Any]) -> str:
    return "NEEDS REVIEW" if recipe.get("needs_human_review") or recipe.get("uncertainties") else "READY TO IMPORT"


def recipe_record(candidate: dict[str, Any], metadata: dict[str, Any], recipe: dict[str, Any], transcript: str) -> list[Any]:
    creator = metadata.get("creator_handle", "") or metadata.get("creator_name", "")
    return [
        candidate["row"], candidate["url"], creator, recipe.get("title_en", ""), recipe.get("title_pt", ""),
        recipe.get("primary_category", ""), recipe.get("diet_label", ""), recipe_status(recipe),
        "YES" if transcript else "NO", len(metadata.get("caption", "") or ""), len(transcript),
        json.dumps(recipe.get("ingredients_en", []), ensure_ascii=False),
        json.dumps(recipe.get("ingredients_pt", []), ensure_ascii=False),
        json.dumps(recipe.get("steps_en", []), ensure_ascii=False),
        json.dumps(recipe.get("steps_pt", []), ensure_ascii=False),
        recipe.get("nutrition_assessment", ""),
        json.dumps(recipe.get("substitutions", []), ensure_ascii=False),
        json.dumps(recipe.get("lighter_swaps", []), ensure_ascii=False),
        json.dumps(recipe.get("equipment", []), ensure_ascii=False),
        recipe.get("image_prompt", ""), metadata.get("caption", "") or "", transcript,
        json.dumps(recipe.get("uncertainties", []), ensure_ascii=False),
        json.dumps(recipe, ensure_ascii=False), now_iso(),
    ]


def upsert_ingest(ws, row_index: dict[str, int], candidate: dict[str, Any], metadata: dict[str, Any], recipe: dict[str, Any], transcript: str) -> str:
    status = recipe_status(recipe)
    record = recipe_record(candidate, metadata, recipe, transcript)
    target = row_index.get(str(candidate["row"]))
    if target:
        ws.update(f"A{target}:Y{target}", [record], value_input_option="RAW")
    else:
        ws.append_row(record, value_input_option="RAW")
        row_index[str(candidate["row"])] = len(row_index) + 2
    return status


def queue_updates(row_number: int, success: bool, status: str = "", error: str = "") -> list[dict[str, Any]]:
    if success:
        return [
            {"range": f"H{row_number}", "values": [["food app"]]},
            {"range": f"D{row_number}", "values": [[True]]},
            {"range": f"F{row_number}", "values": [["Food APP — recipe staged"]]},
            {"range": f"G{row_number}", "values": [[TRACKER_URL]]},
            {"range": f"K{row_number}", "values": [["Needs Review" if status == "NEEDS REVIEW" else "Ready to Import"]]},
        ]
    return [
        {"range": f"H{row_number}", "values": [["food app"]]},
        {"range": f"D{row_number}", "values": [[False]]},
        {"range": f"F{row_number}", "values": [["⚠️ Food recipe extraction failed"]]},
        {"range": f"G{row_number}", "values": [[(error or "unknown error")[:400]]]},
        {"range": f"K{row_number}", "values": [["Needs Research"]]},
    ]


def update_queue(queue_ws, row_number: int, success: bool, status: str = "", error: str = "") -> None:
    queue_ws.batch_update(queue_updates(row_number, success, status, error), value_input_option="USER_ENTERED")


def write_recipe_artifact(candidate: dict[str, Any], recipe: dict[str, Any]) -> None:
    path = OUT_DIR / f"row_{candidate['row']}_{shortcode(candidate['url'])}.json"
    path.write_text(json.dumps(recipe, ensure_ascii=False, indent=2), encoding="utf-8")


def stage_candidate(queue_ws, ingest_ws, row_index, candidate, metadata, summary) -> None:
    try:
        recipe, transcript = build_recipe(candidate, metadata)
        write_recipe_artifact(candidate, recipe)
        status = upsert_ingest(ingest_ws, row_index, candidate, metadata, recipe, transcript)
        update_queue(queue_ws, candidate["row"], True, status)
        summary["success"].append({"row": candidate["row"], "title": recipe.get("title_en") or recipe.get("title_pt"), "status": status})
        print(f"[food-app] staged row {candidate['row']}: {recipe.get('title_en') or recipe.get('title_pt')}")
    except Exception as exc:
        update_queue(queue_ws, candidate["row"], False, error=str(exc))
        summary["failed"].append({"row": candidate["row"], "url": candidate["url"], "error": str(exc)})
        print(f"[food-app] FAILED row {candidate['row']}: {exc}")


def process_chunk(queue_ws, ingest_ws, row_index, candidates, summary) -> None:
    metadata_map = fetch_metadata_chunk([candidate["url"] for candidate in candidates])
    for candidate in candidates:
        stage_candidate(queue_ws, ingest_ws, row_index, candidate, metadata_map.get(shortcode(candidate["url"]), {}), summary)


def process_all(queue_ws, ingest_ws, row_index, candidates, summary) -> None:
    for start in range(0, len(candidates), CHUNK_SIZE):
        process_chunk(queue_ws, ingest_ws, row_index, candidates[start:start + CHUNK_SIZE], summary)


def existing_row_index(ingest_ws) -> dict[str, int]:
    return {
        str(row[0]).strip(): idx
        for idx, row in enumerate(ingest_ws.get_all_values()[1:], start=2)
        if row and str(row[0]).strip()
    }
