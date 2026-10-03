# OPC blog pipeline v2 — design proposal

Status: isolated local prototype, no API run, schedule, publication, or provider change. Tracker: T-904.

## Outcome

Aim for three useful, reviewed articles per week once a small pilot shows that research, editing, imagery, and approval can keep pace. The number is a capacity target, not a reason to publish filler. The first pilot is three drafts, with measured editing time and cost before a recurring run is enabled.

## Existing system and gap

- `blog-generator.yml` is manual-only; its schedule has been paused since 2026-06-26.
- The old generator writes to WordPress. The new OPC blog is served by `opc-website-v1` on Vercel with six local articles; WordPress remains a pass-through for unconverted posts.
- The old script promoted classifier-approved topics to a status that could publish directly, chose random fallback topics, forced keyword/word quotas, and selected Pexels images from search terms. Those are poor gates for useful, factually sound articles.
- The current website article renderer handles paragraphs, headings, lists, and inline links, but has no approved in-body figure block. Both React and generated static HTML must be extended together before any visual-rich new article goes live.

## Proposed stages

1. **Question intake:** gather actual homeowner questions, search queries, approved project observations, and official local guidance. Record original URL/date and reader problem. Social posts may inspire a question; they do not establish a construction fact.
2. **Deduplication:** compare against the 232 legacy WordPress posts and six new articles by canonical slug and similar meaning. Choose update/expand of an existing article when it already answers the question.
3. **Human-selected brief:** state reader decision, the specific OPC expertise needed, approved company facts, three to five claims with primary sources and checked dates, useful internal links, and visual concepts. Require an explicit approved status before paying for a full draft.
4. **Draft:** answer the question with a decision, checklist, comparison, or sequence where useful. No fixed word count, keyword density, city-name quota, or invented OPC experience. Any uncertain code, cost, permit, or legal claim is omitted or flagged for research.
5. **Visual plan:** use a real, cleared OPC photo when it documents work. Add one or two in-body visuals only when they explain something, for example a labeled renovation sequence or bid-scope comparison. Render diagrams with the OPC design tokens and deterministic HTML/SVG. If an AI illustration is used, label it as an illustration; never imply it is an OPC jobsite, client home, permit drawing, or built detail. Keep source/provenance, alt text, caption, and rights with each asset. No automatic Pexels/stock substitution.
6. **Editorial gate:** independently check source URLs, claims, duplicate topic, OPC scope/voice, image truthfulness, alt text, mobile layout, internal links, canonical URL, and Article metadata. Priscila reviews the draft and can request a focused revision. Publication is a separate action for an approved version.
7. **Measure:** record draft and approval counts, edits per article, cost per approved article, duplicate rate, organic visits/search queries, and useful actions. Reassess the three-per-week target after the pilot.

## Publication architecture

Generate a content bundle (brief, article, claim ledger, media manifest) and a draft PR for `opc-website-v1`; build a protected Vercel preview. The approved article enters the existing `frontend/src/blog/posts.json` or a future CMS through a separate release step. Preserve original root-level URLs where an article replaces WordPress. Do not let the old WordPress generator publish new Vercel blog articles.

For in-body visuals, add a small explicit block model such as `{type: "figure", src, alt, caption, provenance, illustrative}`. Render `<figure><img><figcaption>` in `BlogV1.jsx` and the static HTML generator, and validate that assets exist and are cleared. Keep the body text and visual manifest reviewable together.

## Public repository review

[`drazewski/content-workflow-agent`](https://github.com/drazewski/content-workflow-agent) demonstrates a sequence of source analysis, research, editorial style, metadata, review, and Markdown export. It is a small repository with no visible license; use it as an idea reference, not copied code or a production dependency. The existing OPC GitHub Actions/Python/JavaScript system is the practical base. Optional mature checks: [Vale](https://github.com/vale-cli/vale) for style and [lychee](https://github.com/lycheeverse/lychee) for links. Neither verifies construction claims.

## Pilot exit criteria

- Three distinct briefs, each with a clear homeowner payoff and claim/source ledger.
- Three drafts with no fabricated project examples, unsupported numeric claims, or duplicate articles.
- Each visual is genuinely explanatory, correctly labeled, and visually reviewed on phone and desktop.
- A human approves every version before it becomes public.
- Actual time and API cost recorded; weekly cadence chosen only after the pilot.

No recurring run or paid call is enabled by this document or the accompanying safety patch.
