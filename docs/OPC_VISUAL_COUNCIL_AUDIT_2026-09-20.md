# OPC Visual / Content Council Audit — 2026-09-20

Status: implementation review on PR #300 branch only. No merge, publication or owner approval.

## Inputs reviewed
- Priscila's six-card paint review.
- Existing OPC Design System and OPC specialty skill.
- Existing `scripts/content_creator/prompt_builder.py` rule: image prompts must match the slide's specific claim, not merely the overall topic.
- Existing Content Ideas, Niche Questions, Proof Post Candidates, Photo Tracker, competitor board and CONTENT_FORMATS resources.
- Human Academy camera-angle prompt reference supplied by Priscila.
- Current OPC runtime: `opc.py`, `opc_editorial.py`, `opc_media.py`, `opc_contract.py`, `opc_render.py`.

## Findings
1. **Visual-job drift.** The new OPC prompt asked for a fixed four-image pool and allowed cards to reuse those images. This contradicted the older intent-first image rule and produced Card 1/2 and Card 5/6 duplication.
2. **Beauty over teaching.** The image prompt optimized for a consistent attractive South Florida room, but did not require the image to prove the card's teaching point. For lighting, the correct visual is a controlled comparison, not another room photograph.
3. **Global lighting instruction conflicted with comparison cards.** `opc_media.py` demanded one dominant light source globally, making sunny/cloudy/night comparison briefs internally contradictory.
4. **Truth boundary for exact color was under-specified.** AI is appropriate for generic context, but an invented swatch can be misread as a real manufacturer color. Exact product/color identity should prefer a real/reference asset; otherwise illustrate process rather than exact appearance.
5. **Staging quality was not explicit.** A photorealistic prompt can still return worn or dated furniture. Owner review requires current, well-kept staging unless age/wear is part of the story.
6. **Public AI labeling was over-applied.** Provenance belongs in internal metadata and must remain auditable. Consumer creative should not be forced to carry boilerplate unless required by the publishing platform or owner.
7. **Review UX regressed.** The OPC review switched from the established copy-to-chat interaction to JSON download and failed to preserve note-only comments.

## Decisions applied
- Card planning is now visual-job first: “what must the viewer SEE to understand this card?”
- Consecutive reuse is a hard gate unless `intentional_reuse=true`.
- Lighting cards request controlled same-room/same-wall condition comparisons.
- Finish cards prioritize reflectivity/material detail.
- Sampling cards visualize the sampling process and must not claim AI swatches are exact colors.
- Camera-angle grammar is optional and subordinate to teaching intent.
- AI provenance remains in assets/cards.json/private review; public boilerplate is not mandatory.
- Review notes autosave and generate organized copy-to-chat text, including note-only feedback.

## Owner-review paint v2 brief
1. Contemporary room, current/well-kept furniture.
2. Main comparison: same wall/room under sunny, overcast and evening/artificial light.
3. Artificial-light detail is supporting, not a duplicate hero.
4. Matte vs higher-sheen reflectivity comparison.
5. Movable sample/process visual without invented exact paint-color representation.
6. Unique closing/checklist composition.

## Validation gates
- Existing synthetic OPC test suite must pass.
- No consecutive duplicate visual without explicit intent.
- No synthetic/unverified project proof.
- Internal provenance remains materialized.
- Review page keeps owner approval false and supports copy-to-chat.
- Actual v2 output must still be visually inspected; green CI alone is not owner approval.

## Council method applied
The stored **O CONSELHO — OPC Website Launch — Verdict + Method Log (2026-08-25)** was used as the governance rubric: establish ground truth first, inspect actual code rather than trusting prose, attack new findings adversarially, run the zero-dependency test tier, preserve owner-recorded requirements, and never close a visual task from code evidence alone.

This session does **not** have a separately callable O Conselho/AIOX execution service, so this is not a new two-seat blind Council run. It is an implementation audit applying the existing Council method and owner requirements. Final visual closure still belongs to Priscila.
