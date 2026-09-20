# Shared capture, specialized content routes

Status: **routing contract implemented; production adapters not integrated or certified**.
Owner clarification: 2026-09-20. This is part of draft PR #300, not a new production pipeline.

## Scope correction

Brazil News is not OPC. A reusable creation entrypoint must accept a source once,
complete or reuse its source-bound transcription, then route the result to the
selected editorial specialists. Separate Mac/Claude skills remain specialists;
they should not become competing transcription implementations.

The existing Content Studio front door is `content-chief`. Preserve it and the
queue-only semantics of `capture`. Do not create another queue, folder registry,
or automatic publishing path to implement this change.

Keep four independent choices: **destination, editorial family, output language,
and format**. A Portuguese transcript may become an English OPC carousel. An
English transcript may inform Brazil News. A UGC product story is not USA News
merely because the product is sold in the US.

## Intended sequence

1. Existing intake preserves the request, source reference, requested destinations,
   and format. Capture and validate source content once. An existing transcript is
   reused only when its exact source identity is verified. No-speech media remains
   explicitly visual-only; an AI summary is never relabelled a transcript.
2. Resolve destinations after capture. An explicit user destination wins. Otherwise
   a classification proposal must use the topic, purpose, brand brief and footage,
   not language alone. Ambiguous input stays unresolved; never silently choose
   Brazil, OPC, or a shared-drive folder as a convenient fallback.
3. Produce an independent job for each requested destination, referencing the same
   immutable capture. `news:both` means Brazil and USA jobs, not an English review
   toggle on one Brazil publication. A joint Brazil/USA comparison article is a
   distinct editorial scope, not an automatic side effect of choosing both.
4. Each adapter loads its specialty skills, research policy, visual system, source
   and media requirements, output language, and target format. Research may be
   shared when applicable; legal, timing and market claims still need local checks.
5. Only after that adapter's real evidence, media, render, review and filing gates
   pass may its output be described as built. Human approval is separate. Failure
   in one destination must not relabel or contaminate a sibling output.

## Editorial profiles

| Destination | Treatment | Boundary |
|---|---|---|
| Brazil News | Brazil editorial profile; PT-BR publication default; source-backed claims, context, dates and jurisdiction | Not all Portuguese content; retain the registered News format and actual evidence |
| USA News | USA editorial profile; EN-US publication default; source-backed claims and relevant institutions | Not Brazil prompts with a different folder; an override language is allowed |
| Brazil + USA | One capture; two separate editorial jobs, output packages and tracker destinations | Not duplicated transcription and not one translated review artifact called two posts |
| OPC | Short, visual homeowner education, material choices, or verified project proof; OPC brand; EN-US default | Not a generic debunk page; AI illustrations are not completed-project evidence |
| UGC | Creator brief plus product, travel or movement subtype; appropriate hooks, real demonstrations and voice | Not OPC branding or News verdict cards; never invent first-person use, visits or endorsements |
| Stocks, Higashi, Book, AI | Retain registered destination identity and require an appropriate specialist | Contract entries are not proof of implemented generators or validated formats |

The profile names and provisional format lists live in `scripts/content_dispatch.py`.
Canonical destination IDs remain in `scripts/routing.py`; no duplicate ID table is
introduced. Missing UGC render folders or other destination fields stay missing
until verified. The adapter must block filing rather than invent them.

`print` is a registered presentation choice, not the universal editorial identity.
OPC research and sources can remain in the private review pack while the feed uses
concise visual cards. News may use claim/proof pairs when that format is selected.
UGC must not inherit either layout automatically. Travel UGC and product UGC remain
different subtypes. Generic UGC language and subtype are unresolved until its brief
provides them; neither is inferred from transcription language.

## What this checkpoint implements

`Capture` holds a frozen source identity and exact-content digest.
`select_routes` validates explicit selections, expands `news:both`, removes duplicate
routes and rejects ambiguous defaults at the new boundary. Legacy `routing.py`
aliases remain unchanged for older callers.

`build_route_plan` creates isolated destination/profile/format manifests and stable
job keys. `shared_capture_count` describes one supplied capture object, **not a
measurement of a transcription provider call**. A stable key is not by itself a
persistent once-only guard; the production adapter must atomically reserve it.

`dispatch_after_transcription` calls only supplied, registered handlers. It checks
that every selected handler exists before any is called. Handlers receive the same
immutable capture and separate job dictionaries. Callback return is recorded only
as `HANDOFF_RETURNED_NOT_VERIFIED`, never as a finished post or approval. Exceptions
are isolated and retain their type without leaking raw provider details.

The 33 initial tests are synthetic routing/handler fixtures. They do not transcribe,
call paid providers, generate media, validate factual claims, write Drive/Sheets,
run the Mac's installed skills, or prove end-to-end readiness.

## Existing behavior that still needs migration

The following findings were read from `8c5b45077e1d01527f30d3ffee669808780fe16c`.
They are **not fixed in legacy runtime by adding this contract**:

- `capture_pipeline.py` already offers `--projects` to reuse transcription, but its
  detector treats `pt-br`, `voiceover pt`, and `em portugu` as Brazil signals ahead
  of OPC/UGC. Its classifier also lists PT-language content as Brazil. Remove that
  conflation and preserve explicit destinations across all dispatch paths.
- `run_ugc`, `run_stocks`, and `run_higashi` are wrappers around `run_opc`. Changing
  `args.project` is not a specialty editorial implementation. Audit downstream
  analysis, brief, storage, logging, and follow-up hooks before replacing it.
- The single-item `--projects` override, invalid destinations, mutable per-job args,
  and final-route follow-up hooks need integration regressions, not only unit tests
  of a new parser.
- `factcheck_print.yml` / `resolve_inputs.py` currently accept Brazil, USA and OPC,
  not the complete route set. The News generator and renderer still carry
  Brazil/Portuguese defaults. Neither this document nor a profile manifest wires
  UGC or a dual-market output into that workflow.
- OPC filing currently duplicates registry IDs. Move destination resolution to the
  canonical registry while preserving shared-drive support and readback checks.

Affected surfaces to inspect before migration: `scripts/routing.py`,
`scripts/capture/capture_pipeline.py`, capture queue processor and resource router,
`factcheck_print.yml`, `resolve_inputs.py`, `run.py`, `opc.py`, `opc_store.py`,
`render_deck.py`, `cards_runtime.js`, existing per-niche handlers, and private
specialty skills. Mac symlinks and local-only rules have not been changed or synced
by this checkpoint.

## Acceptance evidence required before merge/readiness

| Scenario | Required evidence beyond these unit tests |
|---|---|
| Brazil only | One verified source capture; Brazil research/profile; real resources; readable output; correct News tab |
| USA only | No inherited Brazil-only prompt/layout; US-appropriate context; correct USA tab |
| Both | One measured capture; two isolated packages and receipts; retry one without rebilling the other |
| Portuguese OPC | Remains OPC; registered brand; short copy; actual materialized images; no invented job proof |
| UGC product | Actual brand/product brief, substantiated claims, authorized media and disclosures; no invented experience |
| UGC travel | Actual place/footage identity, original audio, verified facts, preserved real opinions and privacy rules |
| Invalid or ambiguous destination | No paid generation, no guessed folder, no silent fallback |
| No-speech media | Accurate visual-only provenance; no fabricated transcript; suitable specialist |
| Partial failure/retry | Paid step checkpointing, persistent job reservation, isolated statuses and verified filing |

At the prior live checkpoint, run `35535576845` failed: Claude stopped with a
TypeError and OpenAI stopped at editorial/source review. Both recorded zero image
requests. Source-video retrieval remained unavailable; saved transcript reuse did
not prove playable video. Paid retries must resume verified checkpoints rather
than discard usage history or reset guards. Existing synthetic browser checks are
not approval of generated content. Keep this PR draft and unmerged until actual
route outputs meet the acceptance evidence above.
