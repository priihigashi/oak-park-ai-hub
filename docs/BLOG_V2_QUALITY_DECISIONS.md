# Blog v2 quality decision — 2026-10-10

Status: Council round 3 decision with partial implementation. T-904 remains draft-only and recurrence remains held. Three of the five allowed Council rounds have been used.

## Acceptance batch, 2026-10-10

The next autonomous batch selected Content Ideas rows 14 (kitchen exhaust during a full renovation), 98 (HVAC sizing during a room addition), and 4 (retail accessibility). The first two produced 453- and 425-word drafts with clear deterministic gates and independent Claude article-level passes. Both reviewers noted that their Broward framing rests on national sources, so those passes do not establish local editorial usefulness. The third run failed after its one allowed revision: the model added four Florida/Broward/legal source IDs absent from the supplied source set, and cited a DOJ sentence outside the retrieved excerpt. The source and independent review gates blocked it. No draft was published.

Program decision: keep recurrence held. Retain the failed run and reviewer findings in the shared Drive audit; do not weaken the source gate to pass it. Next add verified official local evidence where local claims matter, strengthen the prompt's source whitelist and its regression coverage, then rerun a fresh immutable third candidate. A three-article batch review must confirm distinct reader payoffs, local relevance, source diversity, and useful answers before any one-per-week trial. The Website Build Tracker and shared Council/OCC record contain the editorial decision and audit link.

### Resolution after verified-source rerun

A fresh row 4 run retrieved the DOJ primer and 2026 Florida Statutes 553.503 and 553.504 from their official sites. The six-claim draft passed the deterministic and independent article checks. Its predecessor's unsupplied-source failure remains in the audit. A separate Claude review of all three fresh articles as a series returned **HOLD**: the same question-list format and CTA recur, direct technical answers are thin, Broward-specific value is weak, the HVAC piece has one source, and no in-body explanatory figures are present. These are program-level failures despite three article-level passes. The full audit and review are in the shared Drive and indexed in T-904.

Proposed gates for testing: format diversity across a batch, direct source-supported answers, relevant local evidence, source diversity, and rights/provenance-checked figures within articles. The reviewer suggested exact counts for publishers and concrete facts. Do not encode those counts until they have been tested against a representative corpus; a fixed fact count could induce irrelevant figures or punish a concise, useful answer. Do not force a context-poor numeric ventilation figure into a draft to satisfy a quota. Correct the retail draft's compressed paraphrase of 553.504 before any publication review. Recurrence, publication, and old WordPress remain off.

## Decision and evidence

Hold recurring generation. Three autonomous pilots selected separate Content Ideas rows after screening 93 raw rows against 239 current and legacy entries. The subjects were a Broward home addition, screen porch enclosure, and retail build-out. All three relied on the same two general Broward County pages: Building Code Division jurisdiction and ePermits OneStop. Claude's independent article-level factual reviews passed with minor notes, while the cross-run assessment found repeated office-identification advice and little service-specific guidance. Two pilot bundles passed the current automated gate. None was published. Article-level factual restraint does not prove a useful three-article series.

## Dissent and resolution

The article-level passes support keeping the drafts as reviewable pilots. They do not support a recurring three-per-week cadence because the source pool and answers are too repetitive. A one-per-week trial was considered and rejected while the current gates still pass thin work. Exact similarity thresholds and minimum source counts remain open to corpus testing; avoid choosing arbitrary numbers that suppress valid topics.

## Proposed versioned rules

1. Require at least one official source directly relevant to each selected service and reader decision; general jurisdiction or portal pages alone cannot support a service-specific article.
2. Compare new candidates and drafts against current, legacy, queued, and recent pilot intent clusters. Use a cluster budget so one answer is not repeated with a different project label.
3. Require each consequential claim to map to a relevant cited passage; reject irrelevant details and source links that merely mention the county.
4. Review the three-article batch for distinct reader payoffs, specific actionable answers, and source diversity. A reviewer finding that the available sources cannot answer the central question blocks advancement.

Implementation state: the intake now requires an explicitly tagged topic-specific source, records rejected candidates, and anchors selected themes to the raw idea. The draft gate enforces a 400-word floor and checks listed claims against cited evidence. A blocked independent review may trigger one bounded revision and a second independent review. Cross-run draft similarity, cluster budgets, program-level batch usefulness review, and recurring cadence remain pending. The pilot records predating these gates remain unchanged. Publication still requires approval of the exact article version and a separate website release.

## Restart and rollback

Restart recurrence only after the rules are implemented and tested, a new autonomous three-article acceptance batch passes independent factual/editorial review and cross-run usefulness review, costs are verified, and the publication interlock is checked. Target three articles per week only while quality holds. To roll back a new rule, revert its Git commit and disable the schedule; preserve pilot bundles, receipts, and review records. Never route a v2 draft to legacy WordPress.
