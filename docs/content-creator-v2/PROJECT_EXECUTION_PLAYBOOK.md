# Reusable Project Execution Playbook

Created: 2026-08-05
Scope: how Athena, Codex, Claude, or a future agent should advance projects without Priscila babysitting every step.

## Why this exists

Priscila repeatedly identified the same failure pattern: a project begins with a strong idea, grows across chats, gets mixed with tools, links, research, Focus rows and repo work, then becomes hard to continue because the workflow lives in fragments.

This playbook captures the formula used in the Content Creator V2 planning session so it can be reused for future apps, pipelines, systems and content workflows.

## The short command contract

When Priscila says `go`, `vai`, `continue`, or asks whether more can be done, the agent should not ask her to restate the project if source-of-truth documents exist.

Instead:

1. Identify the current project.
2. Retrieve the canonical docs and Focus rows.
3. Check the repo/workspace before inventing new work.
4. Advance the next safe block.
5. Save results in durable places.
6. Report exactly what changed, where, and what is next.

## Standard project formula

### 0. Source-of-truth retrieval

Find and read:

- current Google Doc or master plan;
- GitHub docs under the project path;
- relevant Focus rows;
- repo files if coding or architecture is involved;
- prior decisions, gates, and no-touch boundaries.

Do not rely on chat memory alone.

### 1. Intake compression

Write a one-paragraph operational objective:

- what problem is being solved;
- who uses it;
- what output counts as useful;
- what must not happen.

Example: `Create a construction content assistant that finds relevant job footage, proposes shots for a script, lets Priscila approve candidates, and renders a first cut without damaging original media or relying on fragile chat history.`

### 2. Existing-system audit before new build

Before coding, inspect:

- repo entry points;
- workflows;
- scripts;
- docs;
- existing agents/skills;
- storage locations;
- Drive/Sheet dependencies;
- secrets and auth boundaries;
- current failures and disabled workflows;
- tests and CI.

Output a decision table:

`Requirement | Existing file/symbol | Decision | Reason | Allowed package | Risk | Test required`

Allowed decisions:

- REUSE
- EXTEND
- ADAPT
- RECREATE
- REPLACE LATER
- NEW

### 3. Route comparison

For tools, repos, APIs, or workflows, compare routes in this order:

1. MCP or existing connector.
2. Official API.
3. GitHub/open-source/self-hosted.
4. Official CLI/SDK.
5. Browser automation.
6. Manual UI.

Always include the current/repair route when one exists.

### 4. External research gate

Do not accept a Reel, ad, or influencer post as proof.

For each tool/repo/app capture:

- official docs;
- GitHub repo if available;
- license;
- install method;
- API/MCP/SDK availability;
- exportability;
- privacy/data-retention;
- pricing/current limits;
- commercial rights;
- Mac compatibility;
- security concerns;
- smallest pilot;
- rollback.

Classify as MANUAL BRIDGE, BENCHMARK, REFERENCE, ADAPT, ADOPT, or REJECT.

### 5. Durable documentation before implementation

Every lasting decision must be saved in at least two durable places:

- human-readable Google Doc;
- versioned GitHub Markdown;
- Focus row as operational pointer.

Use append-only dated sections. Avoid renaming canonical docs after they are introduced.

### 6. Package work into executable blocks

Each package must include:

- goal;
- files allowed;
- files forbidden;
- exact interfaces/contracts;
- tests;
- acceptance gates;
- commit boundaries;
- rollback/no-op rules;
- handoff format.

### 7. Implementation rule

Implementation begins only after a real Package 0 audit when an existing system is involved.

No new abstraction until the repo has been searched for an existing one.

### 8. Tracker rule

For now, do not create a separate Jira-like tracker for this project unless Focus becomes insufficient.

Use:

- Focus Pending for operational status and next action;
- Google Docs for human-readable plans and synthesis;
- GitHub Markdown for versioned specs and execution files;
- GitHub Issues only when a coding package becomes implementation-ready and needs review/assignment.

### 9. Human-step separation

Separate work into:

- agent-only work;
- Priscila decision;
- Priscila physical/computer step;
- Mike/human dependency;
- paid/account step;
- production-risk step.

Do not block agent-only work on a human step if a useful documentation or audit block can still move forward.

### 10. End-of-block handoff

Every block ends with:

- what was done;
- where it was saved;
- what was not touched;
- links;
- next exact block;
- blockers;
- estimated project readiness update.

## This chat's extracted workflow

The useful meta-flow from this chat was:

1. User describes frustration and project risk.
2. Agent verifies sources/tools instead of assuming.
3. Agent creates durable Google Doc source.
4. Agent creates versioned GitHub Markdown backup.
5. Agent updates Focus rows.
6. Agent scans Pending for related loose ends.
7. Agent separates old-flow reuse from broken-flow carryover.
8. Agent freezes Package 0 before coding.
9. Agent captures manual bridges so posting is not blocked by the perfect system.
10. Agent creates a playbook so the same pattern can be reused.

## Anti-patterns to avoid

- Building a shiny new app before a repo audit.
- Preserving broken old flow because it already exists.
- Starting tool shopping instead of defining the missing layer.
- Saving decisions only in chat.
- Creating a second competing tracker.
- Touching production when the requested work is planning or audit.
- Putting personal media, cache, secrets or huge generated assets into GitHub.
- Reporting `done` without a durable link or verification.

## Next use

For Content Creator V2, the next execution step is:

1. Read this playbook.
2. Read SOURCE_OF_TRUTH_AND_STORAGE.md.
3. Read ATHENA_FOCUS_HANDOFF.md.
4. Read PLANNING_CLOSURE_CHECKLIST.md.
5. Read EXTERNAL_APPS_AND_REPOS_RESEARCH_PLAN.md.
6. Read Focus rows 1104–1114.
7. Execute Package 0 and create CODE_AUDIT.md + STATUS.md.
