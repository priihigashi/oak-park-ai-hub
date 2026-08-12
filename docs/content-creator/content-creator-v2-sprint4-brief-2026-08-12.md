# Content Creator V2 — Sprint 4 Concrete Brief
Daily Advancer — 2026-08-12

Master plan doc: https://docs.google.com/document/d/1DjLeV5Ba5jXM4eY-7D0EZSCzzhgCJU8i1u0JDE2lQXU/edit
Coding order step in master plan: steps 5 (script assistant) and 6 (shot planner).

---

## Current state (as of 2026-08-12)

Steps 1–4 are shipped and in /scripts/content_creator_v2/:

Step 1 — contracts.py: MediaAsset, Scene, ShotRequest, ClipCandidate, ApprovedShot, EditDecision schemas
Step 2 — catalog.py + ffprobe.py: SQLite catalog (DEFAULT_DB = ~/.content_creator_v2/catalog.db),
          incremental indexer, checksums
Step 3 — scene_extractor.py, embedder.py: scene detection, keyframes, Whisper transcript,
          visual/text embeddings
Step 4 — search.py + search_cli.py: cosine similarity + keyword + quality boost ranking,
          `ccv2-search` CLI

Sprint 3 goal (plain-language search → relevant construction scenes) is achieved.
Sprint 4 goal: accept a rough script/topic and produce ShotRequest objects per line/beat.

---

## Sprint 4 deliverables

Two new files:
  scripts/content_creator_v2/script_assistant.py  ← step 5
  scripts/content_creator_v2/shot_planner.py      ← step 6

---

## script_assistant.py — step 5 spec

Purpose: accept rough notes, a topic, or a URL and return a structured script with one
visual request per line. Bilingual where needed (English + Portuguese).

Interface:

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ScriptBeat:
    beat_id: str          # stable hash of index + voiceover text
    sequence: int
    voiceover: str        # what is said or shown as text
    visual_query: str     # what visual should accompany this beat
    visual_type: str      # "personal_footage" | "broll" | "screenshot" | "chart" | "generated"
    must_show: list[str] = field(default_factory=list)   # required visual elements
    avoid: list[str]     = field(default_factory=list)   # elements to avoid
    duration_hint: float = 3.0                           # suggested duration in seconds
    citation: Optional[str] = None                       # source for factual claims

@dataclass
class Script:
    script_id: str
    title: str
    language: str           # "en" | "pt" | "bilingual"
    hook: str
    beats: list[ScriptBeat]
    conclusion: str
    cta: str
    raw_input: str          # original notes/topic passed in
    model_used: str
```

Function signature:

```python
def generate_script(
    raw_input: str,
    *,
    language: str = "en",
    target_duration_s: float = 60.0,
    niche: str = "opc",          # "opc" | "brazil" | "usa"
    model: str = "claude-haiku-4-5-20251001",   # cheap model for drafting
    api_key: Optional[str] = None,
) -> Script:
```

Rules:
- The script must NEVER put words in a real person's mouth that are not from a
  documented published source (Claude Rule 2026-08-11 — hard rule, no exceptions).
- For Brazil/political content: mark factual claims with citation field; leave
  citation blank only for structural/opinion beats.
- Hook must be under 10 words (consistent with OPC caption rules).
- Each beat's visual_query should be plain English that the search_cli can use directly.
- Use claude-haiku-4-5-20251001 by default (cheapest Claude model) for script generation.
  The API key comes from ANTHROPIC_API_KEY env var.
- Bilingual output: voiceover in Portuguese, visual_query in English (for search compatibility).

---

## shot_planner.py — step 6 spec

Purpose: convert a Script into ShotRequest objects, search the personal library first,
fall back to public providers. Returns one ClipCandidate per beat (top result).

Interface:

```python
def plan_shots(
    script: Script,
    *,
    db_path: Path = DEFAULT_DB,
    top_k: int = 3,            # candidates per beat, for the approval sheet
    source_filter: Optional[str] = None,
) -> list[tuple[ScriptBeat, list[ClipCandidate]]]:
    """
    For each beat in script.beats:
      1. Call search_scenes(beat.visual_query, ...) against personal library
      2. If fewer than top_k results, extend with stub ClipCandidates
         from public fallback (Pexels/Pixabay — use existing motion_sources.py)
      3. Return (beat, candidates) pairs, best first
    """
```

ShotRequest bridge: translate ScriptBeat → ShotRequest (from contracts.py):

```python
def beat_to_shot_request(beat: ScriptBeat) -> ShotRequest:
    return ShotRequest(
        shot_id=beat.beat_id,
        voiceover=beat.voiceover,
        visual_query=beat.visual_query,
        preferred_source="personal" if beat.visual_type == "personal_footage" else "any",
        fallback_sources=["pexels", "pixabay", "wikimedia"],
        duration_seconds=beat.duration_hint,
        must_show=beat.must_show,
        avoid=beat.avoid,
        orientation="vertical",   # 9:16 default for reels
    )
```

Provider order to enforce (per master plan §8):
  1. PersonalLibraryProvider (search_scenes from search.py)
  2. PexelsProvider (already in motion_sources.py)
  3. PixabayProvider (already in motion_sources.py)
  (WikimediaProvider + ArchiveProvider + YouTubeProvider = Phase 3+, not Sprint 4)

---

## CLI entry point (shot_planner.py)

```
ccv2-plan --input <topic_or_file> [--language pt] [--niche brazil] [--duration 60]
```

Outputs a JSON file: ~/.content_creator_v2/plans/<script_id>.json
Schema: { "script": Script, "shots": [ {"beat": ScriptBeat, "candidates": [ClipCandidate]} ] }

---

## Tests to write (step 10 — Sprint 7)

Sprint 4 test stubs to create now (maya_tests.yml pattern):
  tests/test_script_assistant.py
    - test_generate_script_en: topic "concrete driveway repair", niche "opc", verify
      hook < 10 words, all beats have visual_query, no fabricated person quotes
    - test_generate_script_bilingual: voiceover in pt, visual_query in en
    - test_beat_stable_id: same text input produces same beat_id across calls

  tests/test_shot_planner.py
    - test_plan_shots_empty_catalog: with no catalog data, returns stubs not errors
    - test_beat_to_shot_request: field mapping is correct
    - test_top_k_respected: never returns more than top_k candidates per beat

---

## Dependencies to add

requirements_content.txt additions:
  anthropic>=0.40.0    (already likely present — verify)
  sentence-transformers>=3.0.0  (already needed for embedder.py)

No new dependencies needed for shot_planner.py (uses existing motion_sources.py + search.py).

---

## What does NOT go in Sprint 4

Sprint 5 (approval artifact — step 7) is out of scope:
  - HTML contact sheet with 3 candidates per beat
  - Approve/replace/adjust UI
  - edit_decision.json output

Sprint 4 is complete when:
  - ccv2-plan generates a structured script from a plain-language topic
  - Each beat has a personal-library-first ClipCandidate (or public stub)
  - Output JSON is readable by the Sprint 5 approval builder

---

## Estimated effort

Master plan estimate for Sprint 4: 4–7 focused days.
Current state: contracts + search are solid, so the scaffolding is done.
Realistic estimate now: 2–3 days (script_assistant.py using the Anthropic API,
shot_planner.py wiring search_scenes + motion_sources stubs).
