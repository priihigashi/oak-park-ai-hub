"""Fail-closed contracts for OPC PRINT. No network, credentials or publication.

Feed text is deliberately separate from private evidence. Generated illustrations
never qualify as proof of completed work. News contracts are not changed here.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qs, urlparse, urlunparse

MAX_SLIDES = 8
MAX_SLIDE_WORDS = 35
MAX_HEADLINE_WORDS = 9
MAX_IMAGES = 5
STATUS = "Built, NOT APPROVED"
AI_DISCLOSURE = "AI illustrations; not an OPC project."  # internal provenance phrase; not mandatory public copy
MODELS = ("google/nano-banana-pro", "google/imagen-4", "bytedance/seedream-4.5")
HEADERS = (
    "# Reviews", "Title", "Post Type", "Format", "Content Type", "Status",
    "Drive Folder Link", "Caption", "Hashtags", "Output Link", "Date Created",
    "Research Doc Link", "Original Source Video Link",
)
LAYOUTS = {"cover", "point", "compare", "close"}
CITATION_MARKUP = re.compile(r"</?(?:cite|citation|antml:[\w:-]+)\b[^>]*>|【[^】]*】|[^]*", re.I)
FORBIDDEN = re.compile(r"\b(?:fatos verificados|a alegação|também|deslize|confirmado|bancadas|aguardando aprovação)\b|\bindex\s*=", re.I)
PROMISES = re.compile(r"\b(?:guaranteed|best in florida|we promise|always the best)\b", re.I)


class GateError(ValueError):
    """Output is not eligible for filing as a built/reviewable carousel."""


def plain(value: Any) -> str:
    """Remove model wrappers, not just escape them into visible code."""
    text = str(value or "")
    for _ in range(4):
        decoded = html.unescape(text)
        if decoded == text:
            break
        text = decoded
    text = CITATION_MARKUP.sub("", text)
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1\s*>", "", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]*>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def words(value: Any) -> list[str]:
    return re.findall(r"[\w]+(?:['’-][\w]+)*", plain(value), re.UNICODE)


def canonical_url(value: str) -> str:
    p = urlparse(value.strip())
    if p.scheme != "https" or not p.hostname or p.username or p.password or p.port not in (None, 443):
        raise GateError("Source must be a public HTTPS URL without credentials")
    host = p.hostname.lower().removeprefix("www.").removeprefix("m.")
    if host == "youtu.be":
        vid = p.path.strip("/")
    elif host == "youtube.com":
        vid = parse_qs(p.query).get("v", [""])[0]
        if not vid and p.path.startswith(("/shorts/", "/embed/")):
            vid = p.path.split("/")[2]
    else:
        vid = ""
    if host in ("youtube.com", "youtu.be"):
        if not re.fullmatch(r"[\w-]{11}", vid):
            raise GateError("Invalid YouTube video identifier")
        return f"https://www.youtube.com/watch?v={vid}"
    return urlunparse(("https", host, p.path.rstrip("/"), "", "", ""))


def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", plain(value).lower()).strip("-")[:60]
    if not result or FORBIDDEN.search(value):
        raise GateError("OPC title/slug must be English")
    return result


def safe_relative(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise GateError("Missing/invalid local asset path")
    path = (root / value).resolve()
    if Path(value).is_absolute() or not path.is_relative_to(root.resolve()):
        raise GateError("Asset path escapes its output folder")
    if not path.is_file() or path.stat().st_size == 0:
        raise GateError("Required asset missing or empty")
    return path


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def named_competitor(text: str, aliases: Iterable[str]) -> bool:
    text = plain(text).casefold()
    return any(re.search(r"(?<!\w)" + re.escape(plain(a).casefold()) + r"(?!\w)", text)
               for a in aliases if len(plain(a)) >= 3)


def find_duplicates(rows: list[list[str]], title: str, keywords: list[str], url: str = "") -> list[int]:
    """Header-based topic/URL check; return 1-based sheet row numbers."""
    if not rows or not {"Title", "Original Source Video Link"}.issubset(rows[0]):
        raise GateError("Tracker header unavailable; duplicate check cannot be skipped")
    keys = {plain(k).casefold() for k in keywords if plain(k)}
    if len(keys) != 3:
        raise GateError("Duplicate search requires exactly three distinct topic keywords")
    title_col, url_col = rows[0].index("Title"), rows[0].index("Original Source Video Link")
    target = canonical_url(url) if url else ""
    found = []
    for number, row in enumerate(rows[1:], 2):
        existing_title = plain(row[title_col] if len(row) > title_col else "").casefold()
        old_url = row[url_col] if len(row) > url_col else ""
        try:
            same_url = bool(target and old_url and canonical_url(old_url) == target)
        except (GateError, ValueError):
            same_url = False
        if same_url or existing_title == plain(title).casefold() or all(k in existing_title for k in keys):
            found.append(number)
    return found


def tracker_row(headers: list[str], values: dict[str, Any]) -> list[str]:
    if len(headers) != 13 or set(headers) != set(HEADERS):
        raise GateError("Tracker schema changed; expected the verified 13 headers")
    if values.get("Status") != STATUS:
        raise GateError("No automatic approval or publication status is allowed")
    return [str(values.get(h, "")) for h in headers]


def photo_eligible(row: dict[str, str]) -> bool:
    """READY_FOR_WEB is an allowlist, not an AI interpretation of job identity."""
    all_text = " ".join(str(x) for x in row.values()).casefold()
    return (row.get("Provenance") == "REAL OPC"
            and row.get("Identity Confidence", "").startswith("VERIFIED")
            and row.get("Approval Status") == "APPROVED FOR WEBSITE"
            and bool(row.get("Selected Copy Drive Location"))
            and not any(x in all_text for x in ("quarantin", "light wood kitchen", "day-to-dusk", "twilight", "synthetic")))


def slide_text(card: dict) -> str:
    return " ".join(str(card.get(k, "")) for k in ("headline", "body", "badge"))


def check_copy(card: dict, i: int) -> list[str]:
    text = slide_text(card)
    checks = [
        (card.get("id") == i and card.get("layout") in LAYOUTS, "invalid sequence/layout"),
        (len(words(card.get("headline"))) <= MAX_HEADLINE_WORDS and len(plain(card.get("headline"))) <= 70, "headline too long"),
        (len(words(text)) <= MAX_SLIDE_WORDS and len(plain(card.get("body"))) <= 180, "text too dense"),
        (card.get("badge", "") in ("", "Confirmed", "Needs context"), "inappropriate badge"),
        (plain(text) == re.sub(r"\s+", " ", text).strip() and not FORBIDDEN.search(text), "markup or Portuguese copy"),
    ]
    return [f"slide {i}: {message}" for ok, message in checks if not ok]


def check_sources(card: dict, sources: dict, root: Path | None, middle: bool) -> list[str]:
    errors = []
    if middle and not card.get("source_ids"):
        errors.append("missing factual source")
    for sid in card.get("source_ids", []):
        source = sources.get(sid, {})
        if not source.get("observed_in_search") or not source.get("screenshot"):
            errors.append("source not researched and captured")
        if root and source.get("screenshot"):
            try:
                safe_relative(root, source["screenshot"])
            except GateError:
                errors.append("missing proof screenshot")
    return errors


def check_asset(asset: dict, root: Path | None, proof: bool) -> list[str]:
    errors = []
    if not asset.get("sha256") or not asset.get("path"):
        errors.append("missing materialized visual")
    if asset.get("kind") not in ("ai_illustration", "opc_photo", "licensed_photo"):
        errors.append("unknown visual provenance")
    if asset.get("kind") == "ai_illustration" and asset.get("model") not in MODELS:
        errors.append("unapproved image model")
    if proof and (asset.get("kind") != "opc_photo" or asset.get("identity_verified") is not True):
        errors.append("synthetic/unverified project proof")
    if root and asset.get("path"):
        try:
            path = safe_relative(root, asset["path"])
            if digest_file(path) != asset.get("sha256"):
                errors.append("asset digest mismatch")
        except GateError:
            errors.append("asset cannot be read")
    return errors


def check_deck(spec: dict, aliases: Iterable[str]) -> list[str]:
    cards = spec.get("slides", [])
    text = " ".join(str(spec.get(k, "")) for k in ("title", "caption", "hashtags"))
    text += " " + " ".join(slide_text(c) for c in cards)
    has_ai = any(a.get("kind") == "ai_illustration" for a in spec.get("assets", []))
    checks = [
        (spec.get("project") == "opc" and spec.get("language") == "en", "project/language must be opc/en"),
        (spec.get("status") == STATUS and spec.get("approved") is False, "approval gate missing"),
        (5 <= len(cards) <= MAX_SLIDES, "feed must contain 5-8 slides"),
        (spec.get("kind") in ("education", "project_proof"), "unknown content kind"),
        # AI provenance stays in assets/review metadata. Public copy must not falsely imply an OPC project,
        # but a loud disclosure is not forced unless the publishing platform or owner requires one.
        (not named_competitor(text, aliases), "competitor leaked into public-facing text"),
        (not FORBIDDEN.search(text) and not PROMISES.search(text), "OPC voice/language/promise violation"),
        (spec.get("editorial_review", {}).get("passed") is True, "editorial/coherence review not passed"),
    ]
    return [message for ok, message in checks if not ok]


def validate(spec: dict[str, Any], root: Path | None = None, aliases: Iterable[str] = ()) -> dict[str, Any]:
    """Runtime supplies provenance; model output may not attest its own assets."""
    errors = check_deck(spec, aliases)
    cards = spec.get("slides", [])
    sources = {s.get("id"): s for s in spec.get("sources", [])}
    assets = {a.get("key"): a for a in spec.get("assets", [])}
    if len(assets) != len(spec.get("assets", [])) or len(sources) != len(spec.get("sources", [])):
        errors.append("duplicate source/asset identifiers")
    for i, card in enumerate(cards, 1):
        errors.extend(check_copy(card, i))
        errors.extend(check_sources(card, sources, root, i not in (1, len(cards))))
        errors.extend(check_asset(assets.get(card.get("visual_key"), {}), root, spec.get("kind") == "project_proof"))
        if i > 1 and card.get("visual_key") == cards[i-2].get("visual_key") and not card.get("intentional_reuse"):
            errors.append(f"slide {i}: consecutive visual reuse without explicit intent")
    if errors:
        raise GateError("; ".join(dict.fromkeys(errors)))
    return {"passed": True, "slide_count": len(cards), "max_words": max(len(words(slide_text(c))) for c in cards), "approved": False}


def audit_legacy(spec: dict[str, Any]) -> dict[str, Any]:
    """Measure the actual historic output without inventing failed assertions."""
    claims = [c for c in spec.get("cards", []) if c.get("type") == "claim"]
    counts = []
    for card in claims:
        text = " ".join((card.get(k) or {}).get("en") or (card.get(k) or {}).get("pt", "") for k in ("hd", "say", "chk"))
        counts.append({"id": card["id"], "words": len(words(text))})
    raw = json.dumps(spec, ensure_ascii=False)
    return {"source": "supplied historic cards.json", "cards": len(spec.get("cards", [])),
            "claim_word_counts": counts, "video_present": bool(spec.get("video")),
            "citation_markup_present": bool(CITATION_MARKUP.search(html.unescape(raw))),
            "generated_product_images": len([a for a in spec.get("assets", []) if a.get("kind") == "ai_illustration"]),
            "caption_present": bool((spec.get("caption") or {}).get("en")),
            "screenshot_failure_reported": any("screenshot failed" in str(g) for g in spec.get("gaps", []))}
