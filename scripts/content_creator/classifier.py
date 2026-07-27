#!/usr/bin/env python3
"""
classifier.py — Content Niche + Format Classifier

Phase 1 Task 2 (content-creator-rebuild-phase1-spec.md).
Callable standalone (pipe text in or pass as argument) or imported as a module.

Input:  text (transcript or article body — first 2000 tokens used)
Output: {content_type, niche, format_id, path, confidence, reasoning}

Confidence gate:
  - < 0.75  → path forced to "manual-review" — never auto-routes an uncertain item
  - DRAFT formats (FORMAT-022, FORMAT-023) always → "manual-review"
  - No API key → rule-based fallback, confidence 0.4, always "manual-review"

Source of truth for format definitions: CONTENT_FORMATS Drive doc
  1XqXSyJC_iHMTrmMxpM5ZR7S-WQxz19HhDJO1HomdncM
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

# ── API config ────────────────────────────────────────────────────────────────
_API_KEY = os.environ.get("CLAUDE_KEY_4_CONTENT", "")
_MODEL   = "claude-haiku-4-5-20251001"  # fast + cheap for classification
_API_URL = "https://api.anthropic.com/v1/messages"
_MAX_INPUT_CHARS = 8000  # ≈ 2000 tokens @ 4 chars/token

MANUAL_REVIEW_THRESHOLD = 0.75
_DRAFT_FORMATS = {"FORMAT-022", "FORMAT-023"}

# ── Condensed format registry (from CONTENT_FORMATS Drive doc) ────────────────
# Each entry is a one-liner of key signals for the prompt context window.
_FORMAT_REGISTRY = """
FORMAT-001 (Brazil/USA News, Reel) — Fact-check reel: claim clip + real-time source overlay.
  Keywords: fact-check, verificar, prova, fonte, oficial, votacao, documento, CNN Brasil, Fatos Primeiro.
FORMAT-002 (Brazil News, Carousel) — "Quem realmente decidiu isso?" political accountability chain.
  Keywords: responsavel, culpa, quem fez, quem votou, quem assinou, por que subiu, por que caiu.
FORMAT-004 (Brazil/USA News, Reel/Carousel) — Story/Opinion: real case → structural pattern → data → open question.
  HARD RULE: real video clip required. Keywords: historia real, caso real, ela foi, aconteceu, testemunho.
FORMAT-006 (Brazil News, Carousel) — "A Parte que Ficou de Fora": suppressed context in official narrative.
  Keywords: parte que ficou, o que nao contaram, esqueceram de dizer, contexto, raiz, nao foi noticiado.
FORMAT-007 (UGC, Reel) — Silent Movement Product Showcase: body + product, no face, brand-swap format.
  Keywords: silent UGC, movement, product showcase, no face, body movement, pose swap.
FORMAT-010 (Brazil/USA News, Carousel) — "Todos os Lados": same story from left/center/right outlets.
  Keywords: esquerda, direita, centro, perspectiva, midia, cobertura, vies, Folha, Veja, Jovem Pan.
FORMAT-011 (Brazil/USA News, Carousel) — "A História que Eles Esquecem": suppressed historical context for countries.
  Keywords: historia real, antes de, ditadura, golpe, intervencao, sancao, embargo, contexto historico.
FORMAT-013 (Brazil/USA News, Carousel/Reel) — "Verificamos": automated fact-check series, confidence gate ≥0.70.
  Keywords: fake news, desinformacao, mentira, verificar, checagem, AFP Checamos, Lupa, boato.
FORMAT-014 (Brazil/USA News, Carousel) — "A Conta que Ninguém Pagou": compounding cost of systemic neglect.
  Keywords: custo, sistema penal, desigualdade estrutural, quem paga, ciclo de pobreza, custo social.
FORMAT-015 (Cross-niche, Reel/Video) — "Arquivo Aberto": AI-image narrative + ElevenLabs VO.
  Keywords: nao contada, arquivo, registro, silenciada, historia esquecida, documento revelado.
FORMAT-021 (Brazil/USA News, Carousel 9-10 slides) — Educational Explainer: concept/law/policy at 8th-grade level.
  Pipeline key: educational-explainer. Keywords: explainer, explicar, como funciona, o que e, lei, politica.
FORMAT-022 (Brazil/USA News, Carousel, DRAFT) — "Os Acusados": legal-style evidence carousel (DRAFT — manual review always).
  Keywords: acusado, denuncia, CPI, inquerito, policia federal, prova, documento, investigacao.
FORMAT-023 (Brazil/USA News, Carousel/Reel, DRAFT) — "A Consequencia": causal chain past→present (DRAFT — manual review always).
  Keywords: consequencia, resultado, o que aconteceu depois, impacto, efeito, anos depois.
FORMAT-024 (Brazil News, Carousel 5 slides) — "Defesa Etimológica": debunks viral false Portuguese etymology on WhatsApp/Instagram.
  Keywords: etimologia, origem da palavra, significa, acronimo, sigla, mentira linguistica.
OPC-tip (OPC, tip) — Oak Park Construction product/service education tip carousel. Pipeline key: tip.
  Signals: construction tip, how to, concrete, renovation, bathroom, kitchen, drywall, contractor, Florida, driveway, patio, stucco.
OPC-progress (OPC, carousel) — OPC before/after or project progress post. Pipeline key: progress.
  Signals: before/after, project complete, job site, transformation, photos of completed work.
""".strip()

_NICHE_SIGNALS = """
OPC       — Oak Park Construction, Mike (the contractor), CBC1263425, renovation, concrete, Florida contractor,
            driveway, patio, stucco, pool deck, bathroom remodel, kitchen remodel, drywall, permit.
Brazil    — Brazilian Portuguese language, Lula, Bolsonaro, PT-BR subtitles, Folha, Veja, Senado, Câmara,
            IBGE, CNJ, real brasileiro, Brazil politics, direitos, eleição.
McFolling — Airbnb, vacation rental, McFolling Properties, Michael (property manager), guest, booking, short-term rental.
News      — Breaking news, geopolitical, USA politics, Congress, verified external sources, international headlines.
UGC       — User-generated content, brand swap, movement template, no face, content creator collabs.
Higashi   — Higashi site, Alexandra Higashi, Higashi real estate (NOT Oak Park Construction).
Stocks    — Stocks, investing, options, ETF, NU, S&P 500, Warren Buffett, portfolio management.
General   — Anything that does not clearly match the above niches.
""".strip()


# ── Public API ────────────────────────────────────────────────────────────────

def classify(text: str, api_key: str = "") -> dict:
    """
    Classify a source text into {content_type, niche, format_id, path, confidence, reasoning}.

    Args:
        text:    Source text (transcript or article body). Truncated to ~2000 tokens internally.
        api_key: Anthropic API key. Falls back to CLAUDE_KEY_4_CONTENT env var.

    Returns a dict with these keys:
        content_type  — "carousel" | "reel" | "blog" | "tip"
        niche         — "OPC" | "Brazil" | "McFolling" | "News" | "General" | "Higashi" | "Stocks" | "UGC"
        format_id     — "FORMAT-XXX" | "OPC-tip" | "OPC-progress" | null
        path          — "content-queue" | "inspiration-library" | "manual-review"
        confidence    — 0.0–1.0
        reasoning     — one-sentence explanation of the top classification signal
    """
    key = api_key or _API_KEY
    if not key:
        return _rule_based_fallback(text)

    truncated = text[:_MAX_INPUT_CHARS]
    system_msg = (
        "You are a content-classification agent for a social media pipeline. "
        "Classify the given source text and return ONLY a JSON object — no markdown, no explanation. "
        "Prefer 'manual-review' over any wrong guess. If uncertain about niche or format, lower confidence."
    )
    user_msg = f"""Classify this source text for a social media content pipeline.

NICHE SIGNALS (choose ONE niche per classification):
{_NICHE_SIGNALS}

FORMAT REGISTRY (match the single best format, or null):
{_FORMAT_REGISTRY}

RULES:
1. niche: one of  OPC | Brazil | McFolling | News | General | Higashi | Stocks | UGC
2. content_type: one of  carousel | reel | blog | tip
3. format_id: best-matching code from the registry (e.g. "FORMAT-002", "OPC-tip") — or null if no clear match
4. path:
   • "content-queue"        → clear niche + format match, confidence ≥ 0.75
   • "inspiration-library"  → good idea but needs development or no exact format match
   • "manual-review"        → confidence < 0.75 OR format is DRAFT OR ambiguous niche
5. confidence: 0.0–1.0 float
6. reasoning: one sentence on the strongest signal that drove the classification

CRITICAL: confidence < 0.75 → path MUST be "manual-review". Unknown niche → General + manual-review.

SOURCE TEXT:
{truncated}

Return ONLY this JSON:
{{
  "content_type": "...",
  "niche": "...",
  "format_id": "...",
  "path": "...",
  "confidence": 0.0,
  "reasoning": "..."
}}"""

    payload = json.dumps({
        "model":      _MODEL,
        "max_tokens": 300,
        "system":     system_msg,
        "messages":   [{"role": "user", "content": user_msg}],
    }).encode()

    req = urllib.request.Request(
        _API_URL,
        data=payload,
        headers={
            "x-api-key":         key,
            "anthropic-version": "2023-06-01",
            "Content-Type":      "application/json",
        },
    )
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
        raw  = resp["content"][0]["text"].strip()
        result = _parse_json(raw)
        return _apply_gates(result)
    except Exception as exc:
        print(f"  [classifier] API error: {exc} — rule-based fallback", file=sys.stderr)
        return _rule_based_fallback(text)


def classify_batch(texts: list[str], api_key: str = "") -> list[dict]:
    """Classify multiple texts sequentially. Returns one result per input."""
    return [classify(t, api_key=api_key) for t in texts]


# ── Internal helpers ──────────────────────────────────────────────────────────

def _parse_json(raw: str) -> dict:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(l for l in cleaned.split("\n") if not l.startswith("```")).strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        m = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if m:
            parsed = json.loads(m.group(0))
        else:
            raise
    for field in ("content_type", "niche", "format_id", "path", "confidence", "reasoning"):
        parsed.setdefault(field, None)
    if parsed["format_id"] in (None, "null", "", "None"):
        parsed["format_id"] = None
    try:
        parsed["confidence"] = float(parsed["confidence"] or 0.0)
    except (TypeError, ValueError):
        parsed["confidence"] = 0.0
    return parsed


def _apply_gates(result: dict) -> dict:
    """Enforce confidence gate and DRAFT-format gate."""
    if result.get("confidence", 0.0) < MANUAL_REVIEW_THRESHOLD:
        result["path"] = "manual-review"
    if result.get("format_id") in _DRAFT_FORMATS:
        result["path"] = "manual-review"
    return result


def _rule_based_fallback(text: str) -> dict:
    """Keyword fallback when API is unavailable. Always returns manual-review."""
    tl = text.lower()
    opc_score = sum(kw in tl for kw in [
        "oak park", "construction", "concrete", "renovation", "bathroom",
        "kitchen", "drywall", "contractor", "driveway", "patio", "stucco", "cbc1263425",
    ])
    brazil_score = sum(kw in tl for kw in [
        "lula", "bolsonaro", "brasil", "senado", "câmara", "ibge", "cnj",
        "folha", "veja", "jovem pan", "governo federal", "eleição", "pt-br",
    ])

    if opc_score >= 3:
        niche, content_type = "OPC", "tip"
    elif brazil_score >= 3:
        niche, content_type = "Brazil", "carousel"
    else:
        niche, content_type = "General", "carousel"

    return {
        "content_type": content_type,
        "niche":        niche,
        "format_id":    None,
        "path":         "manual-review",
        "confidence":   0.4,
        "reasoning":    "Rule-based fallback (API unavailable) — manual review required.",
    }


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="Classify source text for the content pipeline. Reads from stdin or argument."
    )
    ap.add_argument("text", nargs="?", default="", help="Text to classify (or pipe via stdin)")
    ap.add_argument("--key", default="", help="Anthropic API key (overrides CLAUDE_KEY_4_CONTENT)")
    args = ap.parse_args()

    source = args.text or sys.stdin.read()
    if not source.strip():
        print("Error: no text provided (pass as argument or pipe via stdin)", file=sys.stderr)
        sys.exit(1)

    out = classify(source, api_key=args.key)
    print(json.dumps(out, indent=2, ensure_ascii=False))
