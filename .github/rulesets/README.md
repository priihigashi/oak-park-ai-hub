# Branch rulesets

## `main-require-quality-gate.json`

Turns the JS/TS Quality Gate from *"CI that reports red"* into an actual gate.

**Live status, 2026-08-11:** ruleset `20720805` is active on `main`, requires
`ESLint complexity` + `Remotion typecheck`, and has `bypass_actors: []`.
A deliberately failing probe PR was blocked from merge, so the gate is proven to
bind rather than merely display red.

### Apply / inspect / rollback

Apply the version-controlled ruleset only if no active copy exists:

```bash
gh api -X POST repos/priihigashi/oak-park-ai-hub/rulesets \
  --input .github/rulesets/main-require-quality-gate.json
```

Verify:

```bash
gh api repos/priihigashi/oak-park-ai-hub/rulesets --jq '.[] | "\(.id) \(.name) \(.enforcement)"'
```

Update an existing ruleset:

```bash
gh api -X PUT repos/priihigashi/oak-park-ai-hub/rulesets/<ID> \
  --input .github/rulesets/main-require-quality-gate.json
```

Rollback only for an explicit emergency decision:

```bash
gh api -X PUT repos/priihigashi/oak-park-ai-hub/rulesets/20720805 \
  -f enforcement=disabled
```

### What it does

| Rule | Effect |
|---|---|
| `required_status_checks` | `ESLint complexity` and `Remotion typecheck` must pass before a PR can merge |
| `deletion` | `main` cannot be deleted |
| `non_fast_forward` | no force-pushing `main` |

### Bypass findings — measured, not inferred

An earlier config prescribed the GitHub Actions integration as a bypass actor.
The API rejected it on this user-owned repository:

```
422 Validation Failed
Actor GitHub Actions integration must be part of the ruleset source or owner organization
```

`RepositoryRole` actors do validate, but using a write/admin role as a bypass
would also exempt human/agent writers. That defeats the purpose of the gate, so
**do not add a bypass actor**. `enforcement: "evaluate"` was also rejected here;
it requires Enterprise.

Ruleset required-status-checks also apply to direct pushes. This was verified by
an admin direct push to `main`, which GitHub rejected with:

```
2 of 2 required status checks are expected
```

### What DOES NOT work — do not rebuild it

The temporary-ref/prevalidated-SHA design from PR #239 was falsified after
merge. The experiment pushed a commit to a temporary branch, obtained
`success` for **both required checks on that exact SHA**, then attempted to push
that same SHA to `main`. The ruleset still rejected the direct push with:

```
2 of 2 required status checks are expected
```

Classic branch-protection troubleshooting guidance about pre-existing status
checks does not describe this repository-ruleset push behavior. PR #241 replaced
that design. The current helper name `push_prevalidated_main.sh` is historical;
**read its implementation, not the old name** — it now opens and merges a PR.

### The working design — bots go through a PR

`scripts/ci/push_prevalidated_main.sh` now does:

```
commit locally
  -> push to bot/<label>-<run_id>
  -> open PR against main
  -> pull_request event runs the required gate
  -> wait for BOTH named checks on the exact PR head SHA
  -> merge the PR only when both are success
  -> delete the temporary bot branch
```

This route was proven from a laptop/admin principal with PR #240. The helper
itself then received an in-runner self-test because the real workflows use
`GITHUB_TOKEN`, which is a different and weaker principal.

### 🔴 ONE MANUAL REPOSITORY SETTING IS STILL REQUIRED

The in-runner self-test correctly failed with:

```
pull request create failed: GraphQL:
GitHub Actions is not permitted to create or approve pull requests (createPullRequest)
```

The repository Actions setting currently reports
`can_approve_pull_request_reviews: false`. Despite its name, that setting also
governs PR creation by GitHub Actions. Until it is enabled, the three automated
writers fail **loudly** instead of silently claiming success.

Enable it with:

```bash
gh api -X PUT repos/priihigashi/oak-park-ai-hub/actions/permissions/workflow \
  -F default_workflow_permissions=write \
  -F can_approve_pull_request_reviews=true
```

or in the UI:

**Settings → Actions → General → Workflow permissions →
“Allow GitHub Actions to create and approve pull requests”.**

Then prove the runner path instead of assuming it:

```bash
gh workflow run bot_route_selftest.yml
gh run watch "$(gh run list --workflow=bot_route_selftest.yml --limit 1 --json databaseId --jq '.[0].databaseId')"
```

A green run means a real `GITHUB_TOKEN` bot commit reached `main` through a PR
and the required gate. Delete `bot_route_selftest.yml` after that one successful
proof.

### Automated writers that depend on this route

| Workflow | Schedule | Writes |
|---|---|---|
| `nonnegotiables.yml` | daily 02:00 America/New_York | `NONNEGOTIABLES.md` |
| `ads_pulse.yml` | Mondays 08:00 ET | `docs/dashboard/*.html` |
| `ads_approval_watcher.yml` | every 6h | `.github/agent_state/ads_api_approved.json` only on state change |

All three must use `contents: write` + `pull-requests: write` and the shared
helper. The old false-all-clear paths were corrected: a failed commit/push/PR
must make the workflow red; “nothing to commit” is the only benign no-op.

### Proof the human gate binds

A throwaway PR with one deliberately over-threshold function produced
`ESLint complexity: fail` → PR `BLOCKED` → `gh pr merge` refused with
*"the base branch policy prohibits the merge"*. The probe branch was deleted and
`main` never received the file.

### Why `quality-js.yml` has no `paths:` filter

A required check that is skipped by a workflow-level path filter never reports a
conclusion. GitHub can leave the PR at *"Expected — waiting for status"*
indefinitely. PR #235 removed those filters before the checks became required.
**Do not re-add them while these contexts are required.**

### Keep context names synchronized

The ruleset `context` values must exactly equal the job `name:` values in
`quality-js.yml`:

- `ESLint complexity`
- `Remotion typecheck`

Renaming a job without updating the ruleset leaves a required context that never
reports and can deadlock every PR.
