# Content Creator Rebuild — Phase 1 Action Brief
Daily Advancer · 2026-07-20

Source plan: https://docs.google.com/document/d/1sGQ33UJ5CZFcssP8GVs4viP9H1eaeAjD4bGoHTJ-cu0
Status as of 2026-07-20: Phase 0 done (all crons paused), Phase 1 not started.

---

## What Phase 1 is and why it comes before Phase 2

Phase 2 (the story-arc planner — the new brain) only works if two things are already reliable:
1. Transcription: when Priscila drops a source URL, Whisper produces real readable text.
2. Classification: the system can read that text and reliably output {content_type, niche, format_id, path}.

If transcription is broken or classification guesses wrong, the Phase 2 story-arc planner has nothing real to reason about. Phase 1 is the foundation — short, targeted, verifiable.

---

## Phase 1 tasks — concrete implementation steps

### Task 1: Transcription end-to-end test

Goal: confirm a source URL → Whisper → real transcript text works without manual intervention.

Step 1. Pick a test URL: a YouTube video that's been captured before (check Inspiration Library for a row with a YouTube URL and known transcript). This avoids new Apify quota spend.
Step 2. Run the current capture pipeline manually via workflow_dispatch on `capture.yml` (or the equivalent script) with that URL.
Step 3. Check the output: does the transcript column in the sheet contain actual words, or is it blank / "None" / an error string?
Step 4. If broken: check the Whisper job logs in GitHub Actions for the error. Common failures: (a) audio download fails (Apify None-type — see SKILL_fix_apify_none_type.md), (b) Whisper times out on long videos (use chunking), (c) transcript writes to wrong cell.
Step 5. Fix and re-run until 1 URL → 1 clean transcript. Log the test URL and result in this doc.

Done when: one full end-to-end run produces a non-empty, human-readable transcript for a known video URL.

---

### Task 2: Build the classifier

Goal: given a source text (the transcript or article body), output {content_type, niche, format_id, path} with confidence score.

Current state: classification is either missing or handled by a single LLM prompt that often misclassifies (treats Brazil news as OPC, misses niche cues, defaults to "carousel" for everything).

Implementation spec:

Input: transcript or article text (first 2000 tokens is enough; full text wastes tokens)
Output JSON:
```json
{
  "content_type": "carousel | reel | blog | tip",
  "niche": "OPC | Brazil | McFolling | News | General | Higashi | Stocks | UGC",
  "format_id": "FORMAT-NNN or null if no match",
  "path": "content-queue | inspiration-library | manual-review",
  "confidence": 0.0–1.0,
  "reasoning": "one sentence"
}
```

Confidence gate: if confidence < 0.75 → path = "manual-review", do NOT route automatically.

The prompt should:
1. Include a summary of each niche's key signals (OPC = construction/Oak Park/Mike; Brazil = Brazilian politics, PT-BR subtitles; McFolling = Airbnb/vacation rental; News = breaking news, verified sources required).
2. Reference the CONTENT_FORMATS registry (Drive doc 1XqXSyJC_iHMTrmMxpM5ZR7S-WQxz19HhDJO1HomdncM) to match a FORMAT-ID. Pull only the first ~2000 chars of that doc as a lookup table in the prompt.
3. NOT default to any niche or format when unsure — prefer "manual-review" over a wrong guess.

Implementation location: `scripts/content_creator/classifier.py` (new file). Callable standalone or as a step in the pipeline after transcription.

---

### Task 3: Success check

Run 3 test sources through Task 1 + Task 2 end-to-end:
- Test A: a Brazil political video → must classify as Brazil / carousel / FORMAT-002 or similar
- Test B: an OPC construction tip URL → must classify as OPC / tip carousel / FORMAT-010 (once the FORMAT-010 conflict is resolved per OPC_DESIGN_SYSTEM.md note)
- Test C: a general article → must classify as General / blog or manual-review (not force a niche)

All 3 must land on the correct niche and content type. If any misclassify → fix the classifier prompt before Phase 2.

---

## What NOT to do in Phase 1

- Do NOT rebuild the template-fill logic yet (that's Phase 2 + 3).
- Do NOT re-enable any crons until Phase 2 is complete and tested.
- Do NOT touch the WordPress blog publish step yet (separate side fix, independent of this chain — see plan doc).
- Do NOT run Phase 2 story-arc planner until Tasks 1 + 2 + 3 above all pass.

---

## Recommendation on Phase 2 timing

The plan doc asks: Phase 2 (story-arc planner, prototype on Wealth/Power deck) vs Phase 1 (transcription+routing)?

**Recommendation: Phase 1 first, then Phase 2 immediately after.**

The Wealth/Power carousel is a perfect Phase 2 prototype candidate — it's already fully written and sourced (Drive doc 1CMNWtLVyBw5cgcSP7VEitxL2At8XdwgdH5AgpSExolo), so you can feed the slide text as the "story skeleton" and test whether the planner would have produced the same arc autonomously. That makes it a zero-risk test: you know what the correct output should look like.

Do Phase 1 first (probably 1–2 sessions) → then immediately prototype Phase 2 on the Wealth/Power deck → if the arc planner reproduces the deck's structure correctly, it's ready for a fresh source.
