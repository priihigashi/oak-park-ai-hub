# OPC Blog v2 — operating decision (2026-10-10)

Status: **publication 0/week; one private drafting attempt each Monday at 9:00 AM America/New_York.** A three-article series passed independent review for a private trial with no major/blocker findings. The Codex app heartbeat is active; it cannot approve or publish an article. No paid API is active. Exact-version human approval and the React/Vercel release gate still control any public post.

## Cadence and quality decision

Target **one approved article per week**, and skip a week when the evidence or OPC's own insight is insufficient. This is a quality and review-capacity cap, not a claim that posting frequency produces a number-one ranking. Reassess after four weeks of actual operation using accepted/rejected drafts, review minutes, factual corrections, qualified Search Console clicks and leads. Consider two per week only if those measures show a second distinct, useful article can pass without weakening review; do not target three per week from the present pilot evidence. Generation can prepare a spare draft, but publication never occurs on a timer or approval timeout.

The prior `blog-generator.yml` schedule has been paused since 2026-06-26. Its Claude/OpenAI API path created WordPress drafts and its most recent June 26 runs failed. V2 uses autonomous topic selection with duplicate-intent and source gates, Codex drafting, independent Claude article and series review, immutable receipts, and a local review preview. Its current draft PR has no publisher. The React/Vercel site is the intended destination after an exact-version human approval and separate release. Preserve legacy WordPress URLs; never re-enable the old generator as the V2 publisher.

## Company knowledge and writing standard

`scripts/company-info.js` is the existing company knowledge source. V2 now loads its core services, within-project trades, excluded jobs, and voice in the drafting and independent review prompts; the brief stores a digest of that snapshot. The selector checks service aliases against the actual core-service list. A deterministic gate rejects a positive OPC promise to offer standalone roofing, plumbing, or electrical work. Treat company knowledge as a scope boundary, not evidence for a new project, license, price, or outcome claim. Those require their own verified record.

Choose a question that one of the actual OPC services can answer. The article should deliver a concrete reader decision and a usable ending, with local detail only where a topic-relevant local source supports it. Vary the editorial format and use a calm contractor voice. Keep a single natural CTA where appropriate. Do not invent a customer, jobsite, photograph, price, timeline, code result, or guarantee. Update an existing article when it already answers the question. Search ranking is an outcome to measure, not a promise to make.

## Model and cost route

The tested route is the existing authenticated Codex CLI plus Claude CLI subscriptions on the Mac. It produced real private pilots with independent review. Subscription usage limits and the cost of the plans still apply; the pilot did **not** prove that API credits exist or that GitHub Actions can use the subscription credentials unattended. GitHub contains API secret **names**, but their values, balances, and billing state were not inspected. No paid API call was made for V2.

If unattended cloud drafting becomes necessary, use an explicit API mode with a spending cap only after a billing and credential test. At the official list prices checked on 2026-10-10, GPT-5.4 is **$2.50 input / $15 output per million tokens** and Claude Sonnet 5 is **$2 input / $10 output per million tokens**. At an *illustrative* 100,000 input and 20,000 output tokens **per model** for a draft/review workflow, text-model cost is about **$0.95 per candidate** or **$3.80 for four**. A repair, series review, research tools, image processing, and failed candidates add cost. This is arithmetic, not metered OPC spend or a quote; model choice and actual token counts remain unmeasured. Start with the subscription route and measured logs; do not silently fall back to a paid or cheaper model. Sources: [OpenAI model pricing](https://developers.openai.com/api/docs/models/gpt-5.4), [Claude model pricing](https://www.anthropic.com/news/claude-sonnet-5).

## Image decision and two-stage release

1. Draft and review the article first. Propose a visual only when it explains the article or documents actual OPC work.
2. Search the existing OPC Shared Drive photo catalog and approved site/portfolio manifest for a **specific cleared asset** matching service, project, phase, and factual claim. Record source file, project, rights/consent, privacy check, edits or AI use, caption, alt, and exact derivative. Keep originals untouched and strip location metadata from web derivatives.
3. The Apple Photos app is readable interactively on this Mac, but the Photos-to-Drive bridge has documented sync, GPS, duplicate, and permission failures. A GitHub cloud job has no justified access to this local library. A Mac-on photo search is an optional second stage; it queues a candidate for review and never releases an article automatically when the computer wakes.
4. If no relevant OPC photo is cleared, use a genuinely useful original diagram after separate factual and visual approval, a licensed image clearly marked as illustrative, or no in-body image. Never use a generic photo as though it were an OPC project. The site requires approved figure metadata and a matching in-body marker before production rendering.
5. After the final article **and** media are fixed, obtain human approval for that exact content and asset version, then release through the React/Vercel workflow. Any edit voids approval. Missing image rights, source evidence, or approval keeps the item in review.

The Drive folder `Mikes Photos & Videos` and OPC portfolio assets exist, but this audit did not clear a specific new image for any pilot. The historical photo export report documents the bridge failures. The separate PhotoKit/Apple Photos work remains a different project and is not a dependency for the blog.

## Rollout, measurement, and rollback

The weekly private draft attempt was enabled only after three distinct pilots passed individual and independent series review with no major/blocker findings. Each future attempt still needs its own service-specific evidence, source-scoped geography, truthful media, and reader-usable result; a weak topic skips the week. A publishing path must enforce exact-version human approval and the site preview/build checks. Record per accepted article: brief, source receipts, company-scope digest, original/revised text, editor findings, media decision, approval hash, release SHA, cost/time, and later search outcome. Keep rejected articles and no-image decisions.

If quality or cost regresses, disable the draft schedule, leave queued work unpublished, and revert the versioned rule or release commit. Preserve immutable audits. The old WordPress generator stays paused.
