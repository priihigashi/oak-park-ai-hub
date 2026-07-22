# Content Creator Rebuild — Phase 1 Technical Spec
# Transcription Verification + Classifier Build

Created: 2026-07-22 (daily-advancer)
Source: docs (1sGQ33UJ5CZFcssP8GVs4viP9H1eaeAjD4bGoHTJ-cu0) + rebuild plan
Status: READY TO BUILD — no blockers; implement in a fresh Codex session

---

## What Phase 1 delivers

Two things that must work end-to-end before Phase 2 (story-arc planner) starts:

1. **Transcription gate** — given a source URL (IG reel, article, YouTube), verify that the
   capture → Whisper pipeline actually produces usable transcript text (not an empty string,
   not "[BLANK_AUDIO]", not an error blob). One test URL run end-to-end is the success check.

2. **Classifier** — given a transcript + source metadata, output a routing decision:
   `{content_type, niche, format_id, path, confidence}`.
   Low confidence → route to "Unrouted" (no guess). High confidence → route normally.

Success check: drop 3 different source types → each lands on the correct format + path with a
real transcript attached. ZERO silent mis-routes.

---

## Classifier output schema

```json
{
  "content_type": "carousel | reel | blog | short_video | unknown",
  "niche":        "opc | brazil | usa | cross | unknown",
  "format_id":    "FORMAT-001 | FORMAT-002 | ... | none",
  "path":         "opc_tip | opc_progress | brazil_news | usa_news | unrouted",
  "confidence":   0.0 to 1.0,
  "reason":       "one sentence why this classification was chosen"
}
```

Confidence gate: `< 0.70` → force `path = "unrouted"`, do NOT guess. Log the low-confidence
item to the `🚨 Pipeline Failures` tab with stage = `CLASSIFIER_LOW_CONFIDENCE`.

---

## Input contract

The classifier receives:

```json
{
  "source_url":    "https://...",
  "source_type":   "instagram_reel | youtube | article | note",
  "transcript":    "full text from Whisper (may be empty string if failed)",
  "capture_notes": "Priscila's notes from Ideas & Inbox comment column (may be empty)",
  "niche_hint":    "brazil | usa | opc | null   (from capture pipeline routing)"
}
```

If `transcript` is empty string or contains only `[BLANK_AUDIO]` / `[MUSIC]` / `[Applause]`
tokens and nothing else → abort classification, log as `TRANSCRIPT_EMPTY`, route to Unrouted.

---

## CONTENT_FORMATS reference

The classifier must match against registered formats in:
`CONTENT_FORMATS` Drive doc `1XqXSyJC_iHMTrmMxpM5ZR7S-WQxz19HhDJO1HomdncM`

Key formats for routing:
- FORMAT-001 — Verificamos fact-check reels (brazil, news)
- FORMAT-002 — "Quem decidiu isso?" carousel (brazil, news)
- FORMAT-010 — DO NOT use for OPC; brazil format only
- OPC: `opc_tip` path or `opc_progress` path (not a FORMAT-ID, uses opc_tip.html / opc_progress.html)

If source maps to OPC content → set `format_id = "none"` and `path = "opc_tip"` or `"opc_progress"`.

---

## LLM call spec (single call, not a chain — Phase 2 adds the chain)

Model: `claude-haiku-4-5` (fast + cheap for classification)
Max tokens: 400
Temperature: 0 (deterministic)

System prompt skeleton:
```
You are a content classifier for a bilingual media operation.
Given a transcript and source metadata, classify the content type, niche,
and which content pipeline path it should take.
Output ONLY valid JSON matching this schema: {content_type, niche, format_id, path, confidence, reason}
confidence must be a float 0.0–1.0. If unsure, set confidence below 0.70.
```

User message: inject `{source_url, source_type, transcript[:3000], capture_notes, niche_hint}`

---

## Transcription verification step (runs BEFORE classifier)

Entry point: `scripts/capture/verify_transcript.py` (new file)

Logic:
1. Given a `capture_id`, read its Whisper output file from Drive or local cache
2. Compute a quality score:
   - Empty string → FAIL (score 0)
   - < 50 chars → WARN (score 0.3) — probably background noise only
   - > 50 chars and < 10% `[tag]` tokens → PASS (score 1.0)
   - ≥ 10% `[tag]` tokens → WARN (score 0.5) — mostly music/applause
3. Log result to `📸 Photo Catalog` tab (new column: "Transcript Quality")
   Values: PASS | WARN:<reason> | FAIL:<reason>
4. Return the transcript text (empty string on FAIL)

---

## Integration point (where this plugs in)

Current pipeline: `content_creator.yml` → `content_creator.py` → template fill (one-shot)

Phase 1 insertion point: **before** template fill, **after** Whisper completes:
```
capture → Whisper → [NEW: verify_transcript.py] → [NEW: classifier.py] → route → Phase 2
```

For now: if classifier outputs `path = "unrouted"`, write a Pipeline Failures row and exit.
Do NOT attempt to fill a template. Phase 2 (story-arc planner) is the next step after routing.

---

## Files to create

| File | Purpose |
|---|---|
| `scripts/capture/verify_transcript.py` | Quality-score a Whisper output |
| `scripts/content_creator/classifier.py` | LLM classification call; returns schema above |
| `tests/test_classifier.py` | At minimum: test low-confidence → unrouted; test OPC source → opc_tip path; test brazil news → FORMAT-001 |

---

## Success criteria (Phase 1 done when all 3 pass)

1. Run `verify_transcript.py` on a real capture → score logged to Catalog tab, no crash
2. Run `classifier.py` on 3 different source types → each gets correct `path`, all confidences logged
3. Low-confidence input → `path = "unrouted"` + Pipeline Failures row written
4. `test_classifier.py` passes with 0 failures in CI

After Phase 1 passes: proceed to Phase 2 (story-arc planner — the chain that replaces one-shot template fill).
