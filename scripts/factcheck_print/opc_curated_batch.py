"""Build two source-checked OPC homeowner carousels without any text-model calls.

The copy/spec is curated in opc_curated_posts_20260921.json from primary-source
research. Runtime re-reads/captures those public sources before any paid image
generation. Paid work is limited to missing Nano Banana Pro images.
Nothing is approved, scheduled, published, deployed or merged.
"""
from __future__ import annotations

import argparse
from difflib import SequenceMatcher
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "capture"))
sys.path.insert(0, str(HERE.parent))

from opc_contract import GateError, STATUS, digest_file, validate
from opc_media import ReplicateImages
from opc_network import screenshot_source
from opc_render import export, review
from opc_store import Store, CAROUSEL_PARENT


SPEC_PATH = HERE / "opc_curated_posts_20260921.json"
MODEL = "google/nano-banana-pro"
READY_STATE = "CURATED_READY_NOT_APPROVED"
BLOCKED_STATE = "CURATED_BLOCKED_NOT_APPROVED"


def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def load_posts() -> list[dict]:
    raw = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    posts = raw.get("posts", [])
    if len(posts) != 2:
        raise GateError("Expected exactly two curated OPC posts")
    return posts


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", choices=["white-paint", "grout-tile"], default="")
    return ap.parse_args()


def run_key(post: dict) -> str:
    return f"pr300-curated-{post['slug']}-20260921"


def find_run(store: Store, key: str) -> dict | None:
    matches = [f for f in store.list_children(CAROUSEL_PARENT)
               if f.get("appProperties", {}).get("opcPrintRun") == key]
    if len(matches) > 1:
        raise GateError("Ambiguous curated run key in Drive")
    return matches[0] if matches else None


def ensure_folder(store: Store, parent: str, name: str) -> dict:
    matches = [f for f in store.list_children(parent)
               if f.get("name") == name and f.get("mimeType") == "application/vnd.google-apps.folder"]
    if len(matches) > 1:
        raise GateError(f"Ambiguous run-owned folder: {name}")
    return matches[0] if matches else store.folder(name, parent)


def download_drive(store: Store, file_id: str, target: Path) -> None:
    from googleapiclient.http import MediaIoBaseDownload
    meta = store.drive.files().get(
        fileId=file_id, fields="id,name,size,md5Checksum", supportsAllDrives=True
    ).execute()
    if int(meta.get("size", 0)) > 30_000_000:
        raise GateError("Curated checkpoint file exceeds bounded size")
    target.parent.mkdir(parents=True, exist_ok=True)
    request = store.drive.files().get_media(fileId=file_id, supportsAllDrives=True)
    with target.open("wb") as stream:
        dl = MediaIoBaseDownload(stream, request)
        done = False
        while not done:
            _, done = dl.next_chunk()
    if hashlib.md5(target.read_bytes()).hexdigest() != meta.get("md5Checksum"):
        raise GateError("Drive checkpoint checksum mismatch")


def captured_source(source: dict, root: Path) -> dict:
    attempts = []
    for candidate in source.get("candidates", []):
        path = root / "resources" / f"proof-{source['id']}.png"
        try:
            shot = screenshot_source(candidate["url"], path)
            excerpt = shot.get("excerpt", "")
            low = excerpt.casefold()
            missing = [phrase for phrase in candidate.get("required", [])
                       if phrase.casefold() not in low]
            if missing:
                attempts.append({"url": candidate["url"], "status": "anchor_mismatch", "missing": missing})
                path.unlink(missing_ok=True)
                continue
            attempts.append({"url": candidate["url"], "status": "captured_and_anchor_checked"})
            return {
                "id": source["id"], "name": source["name"], "url": candidate["url"],
                "heading": shot.get("heading") or source.get("heading", ""),
                "screenshot": str(path.relative_to(root)), "observed_in_search": True,
                "research_method": "ChatGPT primary-source web research + runtime page readback",
                "excerpt": excerpt, "attempts": attempts,
            }
        except Exception as exc:
            attempts.append({"url": candidate.get("url"), "status": "failed", "error_type": type(exc).__name__})
    save(root / "resources" / f"proof-attempts-{source['id']}.json", attempts)
    raise GateError(f"No source page passed runtime anchors for {source['id']}")


def capture_sources(post: dict, root: Path, store: Store, resources_drive: dict) -> list[dict]:
    sources = []
    for source in post["sources"]:
        result = captured_source(source, root)
        sources.append(result)
        store.upsert_run_file(root / result["screenshot"], resources_drive["id"])
    save(root / "resources/evidence.json", {
        "topic": post["title"],
        "research_date": "2026-09-21",
        "research_method": "Primary manufacturer/industry pages selected in ChatGPT web research; each page re-read and screenshot at runtime before image generation.",
        "sources": sources,
    })
    store.upsert_run_file(root / "resources/evidence.json", resources_drive["id"])
    return sources


def text_audit(post: dict, sources: list[dict]) -> dict:
    slides = post["slides"]
    errors = []
    source_ids = {s["id"] for s in sources}
    visual_keys = [s["visual_key"] for s in slides]
    if visual_keys != [f"A{i}" for i in range(1, 6)]:
        errors.append("five distinct sequential visual jobs required")
    if len(set(visual_keys)) != len(visual_keys):
        errors.append("visual keys repeat")
    for slide in slides:
        if not set(slide.get("source_ids", [])).issubset(source_ids):
            errors.append(f"slide {slide['id']} cites unavailable source")
    pairs = []
    for i, left in enumerate(slides):
        for right in slides[i + 1:]:
            a = (left["headline"] + " " + left["body"]).casefold()
            b = (right["headline"] + " " + right["body"]).casefold()
            ratio = SequenceMatcher(None, a, b).ratio()
            pairs.append({"cards": [left["id"], right["id"]], "similarity": round(ratio, 3)})
            if ratio > 0.72:
                errors.append(f"cards {left['id']}/{right['id']} copy too repetitive")
    if errors:
        raise GateError("; ".join(errors))
    return {"passed": True, "slide_count": len(slides), "visual_keys": visual_keys,
            "copy_similarity_pairs": pairs, "approved": False}


def dhash(path: Path) -> int:
    with Image.open(path) as opened:
        im = opened.convert("L").resize((9, 8))
        px = list(im.getdata())
    bits = 0
    for y in range(8):
        for x in range(8):
            bits = (bits << 1) | int(px[y * 9 + x] > px[y * 9 + x + 1])
    return bits


def image_audit(assets: list[dict], root: Path) -> dict:
    hashes = {a["key"]: dhash(root / a["path"]) for a in assets}
    distances = []
    keys = sorted(hashes)
    errors = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            distance = (hashes[a] ^ hashes[b]).bit_count()
            distances.append({"assets": [a, b], "dhash_distance": distance})
            if distance < 7:
                errors.append(f"{a}/{b} are visually too similar")
    if errors:
        raise GateError("; ".join(errors))
    return {"passed": True, "method": "64-bit difference hash; exact/near-duplicate guard only",
            "distances": distances, "approved": False}


def restored_assets(store: Store, resources_drive: dict, root: Path, post: dict) -> tuple[list[dict], list[dict]]:
    children = {f["name"]: f for f in store.list_children(resources_drive["id"])}
    records = []
    if "image-usage.json" in children:
        download_drive(store, children["image-usage.json"]["id"], root / "resources/image-usage.json")
        try:
            records = json.loads((root / "resources/image-usage.json").read_text(encoding="utf-8"))
        except Exception:
            records = []
    by_record = {r.get("key"): r for r in records if r.get("status") == "succeeded"}
    assets = []
    subjects = {v["key"]: v["subject"] for v in post["visuals"]}
    for key in [f"A{i}" for i in range(1, 6)]:
        name = f"{key}.jpg"
        if name not in children or key not in by_record:
            continue
        target = root / "resources" / name
        download_drive(store, children[name]["id"], target)
        rec = by_record[key]
        assets.append({
            "key": key, "path": str(target.relative_to(root)), "sha256": digest_file(target),
            "kind": "ai_illustration", "model": rec.get("model", MODEL),
            "prediction_id": rec.get("prediction_id"), "subject": subjects[key],
            "prompt": "Restored from durable curated checkpoint; original prompt subject retained in curated spec.",
            "style_anchor": None, "restored_from_checkpoint": True,
        })
    return assets, records


def generate_assets(post: dict, root: Path, store: Store, resources_drive: dict) -> list[dict]:
    assets, records = restored_assets(store, resources_drive, root, post)
    existing = {a["key"] for a in assets}
    provider = ReplicateImages(MODEL, root, max_images=5)
    provider.records = records
    for visual in post["visuals"]:
        if visual["key"] in existing:
            continue
        asset = provider.generate(visual["key"], visual["subject"])
        assets.append(asset)
        store.upsert_run_file(root / asset["path"], resources_drive["id"])
        store.upsert_run_file(root / "resources/image-usage.json", resources_drive["id"])
    assets.sort(key=lambda a: int(a["key"][1:]))
    if [a["key"] for a in assets] != [f"A{i}" for i in range(1, 6)]:
        raise GateError("Curated build did not materialize all five visuals")
    return assets


def build_spec(post: dict, sources: list[dict], assets: list[dict]) -> dict:
    return {
        "project": "opc", "language": "en", "kind": "education", "status": STATUS,
        "approved": False, "title": post["title"], "caption": post["caption"],
        "hashtags": post["hashtags"], "slides": post["slides"],
        "sources": [{k: s[k] for k in ("id", "name", "url", "heading", "screenshot", "observed_in_search")} for s in sources],
        "assets": assets,
        "editorial_review": {
            "passed": True, "english": True, "provider": "source-checked-curated",
            "model": "no text-model call", "automated_review_passed": False,
            "independent_council": False,
            "method": "Copy was manually checked against primary sources in ChatGPT; runtime pages were re-read for required anchors before paid image work.",
        },
        "video": None, "source_url": "", "template": "opc_tip / FORMAT-030 visual PRINT",
        "reference_media_status": "not_applicable",
        "motion": {"requested": False, "status": "static_curated", "reason": "Static OPC carousel review."},
        "build_mode": "source_checked_curated_no_text_api",
        "curated_date": "2026-09-21",
    }


def review_probe(path: Path, root: Path) -> dict:
    from playwright.sync_api import sync_playwright
    html = path.read_text(encoding="utf-8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 900, "height": 900})
            errors = []
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.set_content(html, wait_until="domcontentloaded", timeout=120000)
            note = page.locator("[data-note]").first
            note.fill("LIVE REVIEW PROBE")
            page.wait_for_timeout(50)
            text = page.locator("#review-output").inner_text()
            if "LIVE REVIEW PROBE" not in text or "CARD 1" not in text:
                raise GateError("Live review summary did not update while typing")
            page.locator("[data-choice='keep']").first.click()
            page.wait_for_timeout(30)
            text = page.locator("#review-output").inner_text()
            if "Decision: KEEP" not in text:
                raise GateError("Live review decision did not update")
            if errors:
                raise GateError("Review page JavaScript error: " + "; ".join(errors))
            return {"passed": True, "viewport": "desktop_probe_900x900",
                    "live_typing": True, "decision_updates": True,
                    "copy_button_present": page.locator("#copy-review").count() == 1,
                    "mobile_retest_deferred_as_item_5": True}
        finally:
            browser.close()


def build_one(post: dict, store: Store) -> dict:
    key = run_key(post)
    existing = find_run(store, key)
    if existing and existing.get("appProperties", {}).get("state") == READY_STATE:
        return {"slug": post["slug"], "status": "already_ready", "folder": existing.get("webViewLink")}
    if existing:
        folder = existing
    else:
        if store.duplicates(post["title"], post["keywords"]):
            raise GateError(f"Duplicate topic already exists: {post['title']}")
        folder = store.start_run(post["title"], key)
    root = Path("opc-curated") / post["slug"]
    (root / "resources").mkdir(parents=True, exist_ok=True)
    (root / "motion").mkdir(parents=True, exist_ok=True)
    resources_drive = ensure_folder(store, folder["id"], "resources")
    try:
        sources = capture_sources(post, root, store, resources_drive)
        text_report = text_audit(post, sources)
        save(root / "resources/text-audit.json", text_report)
        store.upsert_run_file(root / "resources/text-audit.json", resources_drive["id"])

        assets = generate_assets(post, root, store, resources_drive)
        visual_report = image_audit(assets, root)
        save(root / "resources/visual-uniqueness.json", visual_report)
        store.upsert_run_file(root / "resources/visual-uniqueness.json", resources_drive["id"])

        spec = build_spec(post, sources, assets)
        save(root / "cards.json", spec)
        save(root / "resources/content-gates.json", validate(spec, root, []))
        export(spec, root)
        review_path = review(spec, root)
        probe = review_probe(review_path, root)
        save(root / "resources/review-interaction.json", probe)
        (root / "motion/README.md").write_text("Static curated OPC carousel; no motion claim.\n", encoding="utf-8")

        store.rename_run(folder, post["title"])
        links = store.upload_tree(root, folder)
        content_row = store.file_row(spec, folder, links)
        flow_row = store.flow_row(spec, folder, links)
        receipt = {
            "slug": post["slug"], "content_row": content_row, "flow_row": flow_row,
            "build_mode": spec["build_mode"], "new_text_api_calls": 0,
            "image_requests_total": len(json.loads((root / "resources/image-usage.json").read_text(encoding="utf-8"))),
            "text_audit": True, "visual_uniqueness_audit": True, "review_live_probe": True,
            "approved": False, "published": False, "folder": folder["webViewLink"],
            "review": links["review.html"],
        }
        save(root / "resources/curated-receipt.json", receipt)
        store.upsert_run_file(root / "resources/curated-receipt.json", resources_drive["id"])
        store.finish(folder, READY_STATE)
        return receipt
    except Exception:
        store.finish(folder, BLOCKED_STATE)
        raise


def main() -> None:
    args = parse_args()
    store = Store()
    store.preflight()
    posts = [p for p in load_posts() if not args.only or p["slug"] == args.only]
    results = []
    for post in posts:
        results.append(build_one(post, store))
    print(json.dumps({"results": results, "approved": False, "published": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
