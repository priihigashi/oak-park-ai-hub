# OPC Chat → Review Creation Flow

Status: active build contract for Social Media APP / Carousels. Owner: Priscila.

## Owner interaction
When Priscila explicitly asks ChatGPT to create OPC content, or supplies an Instagram/TikTok/YouTube talking-video link in that context, that request is authority to continue through the normal bounded creation flow. Do not stop for a second confirmation before research, transcription, editorial audit, image generation, rendering or private filing.

Publication, scheduling, merge/deploy, destructive changes, new credentials, or an unbounded/novel paid route remain separate approval gates.

## Chat-facing behavior
The review site is the primary owner-facing surface. Chat should return the private review URL plus only a short status/cost note. Do not force Priscila to review five cards in chat text.

### Idea/topic request
1. Resolve OPC destination.
2. Research primary/official sources.
3. Audit factual claims and copy.
4. Plan each card by visual job.
5. Generate only the necessary assets.
6. Render all OPC themes.
7. Browser-test review behavior.
8. File to existing Marketing/Content Control + Flow Plans.
9. Return review-site URL. Status remains NOT APPROVED.

### Video-link request
1. Treat the URL as inspiration/source, not automatic evidence.
2. Capture/download through the existing source-video route.
3. Transcribe and select the useful segment(s).
4. Research/verify claims with primary/official sources.
5. Continue through the same audit/build/review-site flow.
6. Preserve the source URL and transcript provenance privately.
7. Never imply the source video itself proves a factual claim unless independently supported.

## Durable ChatGPT trigger
Until a dedicated ChatGPT action exists, the connector-safe trigger is the existing owner issue entrypoint:
- `opc-print: <topic>`
- `opc-print: <instagram|tiktok|youtube URL>`

The linked ChatGPT session may create this issue directly after the owner asks for creation. No second confirmation is required.

The issue body may contain non-sensitive instructions only. Do not place private transcripts, credentials, client data or private project media in GitHub.

On success the workflow must comment the private Drive review URL back to the issue so ChatGPT can return it to Priscila.

## Audit gates before READY FOR PRISCILA REVIEW
- Source/claim mapping is explicit.
- Unsupported specificity is blocked.
- Copy is concise homeowner education, not a fact-check article.
- Each card has a distinct visual job.
- Accidental consecutive visual reuse is blocked.
- Controlled repetition is allowed only when the repeated frame demonstrates one changed variable.
- Exact product/color/material identity uses real/reference assets when the visual would be treated as evidence.
- Generic conceptual AI is allowed but may not masquerade as completed OPC work.
- Review page must update the organized review summary immediately as the owner types, even before Keep/Redo.
- Review page must preserve notes locally when browser storage is available and support one-click organized copy-to-chat.
- Mobile browser test is an acceptance gate after the content set is ready.

## Cost/retry behavior
- Do not silently replay paid text/image work.
- Reuse completed checkpoints/assets when a later deterministic step fails.
- Paid model/provider fallbacks are never implicit.
- Routine creation may use the existing bounded provider route once the owner asked to create; novel or materially higher-cost routes require a separate decision.

## Canonical systems
- Product/flow tracker: Creations → Social Media APP — Project Tracker, SM-013.
- Content outputs: existing Marketing Content Control + Flow Plans.
- Code: priihigashi/oak-park-ai-hub, current OPC branch/PR until merged by owner.
- No second carousel app or duplicate task tracker.
