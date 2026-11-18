---
name: template-carousel
description: Create reusable carousel template systems for a topic or series. Use when Priscila asks to create templates for a carousel topic, compare template styles across tools, make News/OPC/Brazil/USA carousel examples, or turn a recurring content format into approved templates.
---

## ⛔ CSS DE CARD — NÃO ESCREVA NADA ANTES DE LER `/art-director`

O bug que ela reportou em 24/09/2026 (*"this has to be fixed on the skill because it's happening every
single time"*) mora aqui: **`cqw` usado no próprio elemento que tem `container-type` resolve contra a
JANELA, não contra o card** — o padding vira 6% do monitor dela e o texto fica minúsculo espremido no
meio. A estrutura obrigatória é sempre DOIS elementos:

```css
.card{container-type:inline-size;aspect-ratio:1080/1350;position:relative;overflow:hidden}
.pad {position:absolute;inset:0;padding:7cqw 7cqw 6cqw;display:flex;flex-direction:column}
```

Todo `cqw` vive dentro de `.pad`, **a seta inclusive**. Piso de tipografia em 1080×1350: headline
≥ 8,5cqw, corpo ≥ 4,6cqw, jargão 3,1cqw, nota 2,7cqw, kicker/rodapé 2,0cqw, safe inset 108px. Nunca
reduza fonte para caber — abre outro card. Rode o gate de overflow antes de publicar.

**Regra completa, checklist e o porquê:** `~/.agents/skills/art-director/SKILL.md`, seção
"O BUG DO CARD QUE ACONTECE TODA VEZ". Não copie a regra para cá — ela deriva.


# Template Carousel

Use this skill when Priscila says things like:

- "create templates for this topic"
- "template carousel"
- "make carousel templates for this series"
- "test tools for this carousel"
- "use my existing templates first"

## Core Rule

Do not make one-off post art and call it a template. A template is reusable, source-aware, and saved where future content-chief sessions can find it.

## First Checks

1. Read the current format entry in `CONTENT_FORMATS.md`.
2. Check Productivity & Routine handoffs for recent instructions.
3. Check existing Drive and Canva template folders before building.
4. Identify the target shared drive:
   - News content -> News shared drive.
   - OPC/Marketing/McFolling -> Marketing shared drive.
   - Higashi/mom site -> Higashi shared drive.

## Storage Pattern

Drafts go flat first:

`<Niche Shared Drive>/Templates/Carousel/`

Only after Priscila approves a style, move/copy it into a topic folder:

`<Niche Shared Drive>/Templates/Carousel/<SeriesName>/<Variant>/`

Do not create the final topic folder tree before approval unless Priscila explicitly asks.

### OPC Folder IDs (verified 2026-04-28)

- Carousel only: `16P2JN74JAAW3HKnmNqPGPrAq7N5jDNii`
- Reels and Shorts: `1jW3WUQEPpfJNgje-4YGyFT4inKgzWrt7`
- Parent folder containing both: `1lyWGwQiUPAVoMzb8vfQ0fBw72M1A2UfR`

## Default Output

Default to 3 visual directions per topic unless Priscila asks for fewer. For fast tests, 2 directions is acceptable.

Each direction should include the same 5-slide structure:

1. Series hook/title.
2. Proof placeholder: video still, official doc crop, or article crop.
3. Explanation/context.
4. Contrast/comparison.
5. Conclusion/source card.

For FORMAT-005 Our Money / Nosso Dinheiro:

- Slide 1 always uses either "What they'd rather spend our money on" or "What they've been cutting lately."
- Pick whichever title hooks better for that receipt.
- If both fit, alternate over time.

## Tool Order

1. Existing templates audit: Drive + Canva saved designs.
2. HTML / Playwright: exact text and final PNG export.
3. Remotion: still carousel or animated companion when proof/video placeholders matter.
4. Nano Banana / Seedream / OpenAI image generation: visual assets/backgrounds only, not final text.
5. Canva existing templates: adapt references, do not generate from scratch first.
6. Canva AI: test-only / last resort.

Ask before running paid image-generation workflows if the user has not already approved spending for that run.

## Design Rules

- Keep exact text in HTML, Remotion, or Canva text layers.
- Do not rely on AI image generation for readable text.
- Use a visible placeholder when the proof slot can accept either video or screenshot.
- Put source text on the same slide as the claim.
- Use official sources first. News outlets are fallback when no official source exists.
- Label proposals, allegations, and pending legal items clearly.
- Do not hide tiny unreadable screenshots. Use a large crop or summarize the key source line with a source strip.

## Deliverables

For each template test, deliver:

- Local draft path.
- Drive destination and link after upload.
- PNG preview/export folder.
- Prompt pack used for AI image/Canva/Remotion routes.
- Recommendation: keep, revise, or discard each direction.

Never stop at HTML only. HTML is the source/editable template; PNGs are the reviewable carousel slides.

Required output set:

- HTML source file for each direction.
- One PNG per slide for each direction.
- Prompt pack or recipe note.
- All files uploaded to the correct shared Drive `Templates/Carousel` folder.

## Repeatable Recipe

When Priscila asks for a new topic:

1. Name the series/topic and choose the content angle.
2. Pull one real source example for the first template.
3. Create 2-3 visual directions using the same slide structure.
4. Build HTML source drafts locally.
5. Export each HTML into PNG slides with Playwright:
   - Use `/Users/priscilahigashi/ClaudeWorkspace/Content Templates/_Scripts/export_slides.js`.
   - Export into a local `_exports/` folder next to the HTML.
6. Upload the HTML, PNG slides, and prompt pack to the shared drive template carousel folder.
7. Give Priscila the shared Drive folder link, HTML links, and the first PNG preview links.
8. Wait for Priscila approval before locking a topic folder.

## Proven Export Path

For local HTML drafts:

```bash
node "/Users/priscilahigashi/ClaudeWorkspace/Content Templates/_Scripts/export_slides.js" "<input.html>" "<output_dir>"
```

If browser launch fails in the sandbox, rerun the same command with elevated permissions. Do not ask Priscila to manually export screenshots.

Upload via OAuth Drive API with `supportsAllDrives=true`. The draft destination for News is:

`News > Templates > Carousel` — folder ID `1z7yJu5K87nEPktyxcWQJgeKKUp-dtyuo`

The draft destination for Oak Park/OPC currently lives in Marketing:

`Marketing > ... > Carousel` — folder ID `16P2JN74JAAW3HKnmNqPGPrAq7N5jDNii`

Reels/shorts destination:

`Marketing > ... > Reels and Shorts` — folder ID `1jW3WUQEPpfJNgje-4YGyFT4inKgzWrt7`

Shared parent containing both folders:

`Marketing > ...` — folder ID `1lyWGwQiUPAVoMzb8vfQ0fBw72M1A2UfR`

## VIDEO LENGTH LIMIT: 60 SECONDS IN A CAROUSEL (her rule 2026-09-19, tested on the INSS deck)
Her words: the video in the first card cannot be longer than 60 (she wrote "minutes"; read as seconds, the Instagram carousel limit); if it is longer, cut or speed it up and learn from it.
1. **Check the duration first** (`ffprobe` / `ffmpeg -i`). <= 60 s: use as is.
2. **Silence removal barely helps a tightly edited speaker** (tested: 2.2 s of silence in 213 s). Use it only for loose footage.
3. **Main lever = segment selection**: from a timestamped transcript keep WHOLE segments that carry the hook and the checked claims, drop explainer repetition and the outro/CTA. Never cut mid-word.
4. **Then speed up comfortably: 1.2x (hard max 1.25x)**, audio with `atempo`. She asked for "a little faster, still comfortable", not a chipmunk.
5. **Remotion** when the cut also needs titles/captions/transitions; plain ffmpeg concat is enough for straight cuts.
6. The full-length original stays in Drive `resources/`; the card plays the <=60 s cut. Tell her in the report: original length -> new length, which parts were dropped.
Tested result: 213 s -> 59.4 s (5 whole segments, 1.2x), deck v10. Code: `oak-park-ai-hub/scripts/factcheck_print/fit_video.py` (probe, whisper timestamps, model picks segments, validate, ffmpeg concat + speed).
