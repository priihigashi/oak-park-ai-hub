# Branch rulesets

## `main-require-quality-gate.json`

Turns the JS/TS Quality Gate from *"CI that reports red"* into an actual gate.

As of 2026-08-11 `main` is `protected: false` with zero rulesets and zero required
status checks — so a PR can be merged while `ESLint complexity` or `Remotion typecheck`
is failing, and `main` can be pushed to directly. This ruleset closes that.

### Apply it

```bash
gh api -X POST repos/priihigashi/oak-park-ai-hub/rulesets \
  --input .github/rulesets/main-require-quality-gate.json
```

Verify:

```bash
gh api repos/priihigashi/oak-park-ai-hub/rulesets --jq '.[] | "\(.id) \(.name) \(.enforcement)"'
```

To update an existing ruleset instead of creating a duplicate, use its id:

```bash
gh api -X PUT repos/priihigashi/oak-park-ai-hub/rulesets/<ID> \
  --input .github/rulesets/main-require-quality-gate.json
```

To roll back:

```bash
gh api -X DELETE repos/priihigashi/oak-park-ai-hub/rulesets/<ID>
```

### What it does

| Rule | Effect |
|---|---|
| `required_status_checks` | `ESLint complexity` and `Remotion typecheck` must pass before merge |
| `deletion` | `main` cannot be deleted |
| `non_fast_forward` | no force-pushing `main` |

### ⚠️ Bypass — corrected 2026-08-11 after applying it for real

An earlier version of this file prescribed `{"actor_id": 15368, "actor_type":
"Integration"}` to exempt GitHub Actions. **That does not work on this repo.**
The API rejects it:

```
422 Validation Failed
Actor GitHub Actions integration must be part of the ruleset source or owner organization
```

`priihigashi/oak-park-ai-hub` is **user-owned, not org-owned**, so `Integration`
bypass actors are unavailable. Only `RepositoryRole` actors validate here
(tested: `5` admin and `4` write both accept; `enforcement: "evaluate"` is also
rejected — it requires Enterprise).

### The unresolved consequence — read before relying on this

`required_status_checks` in a ruleset applies to **direct pushes as well as
merges**. Verified empirically: a direct push to `main` was rejected with
*"2 of 2 required status checks are expected"*, even as a repository admin.

Three workflows push straight to `main` via `secrets.GITHUB_TOKEN`:

| Workflow | Schedule | Pushes |
|---|---|---|
| `nonnegotiables.yml` | daily 02:00 ET | `NONNEGOTIABLES.md` — commits most nights |
| `ads_pulse.yml` | Mondays 08:00 ET | `docs/dashboard/*.html` |
| `ads_approval_watcher.yml` | every 6h | `.github/agent_state/ads_api_approved.json` (only on state change) |

### ✅ RESOLVED (PR #239) — the bots pass through the gate, nobody bypasses it

The write-role bypass was **rejected as a solution**: it would exempt every human
writer as well, in a repo where agent sessions hold write and admin tokens — the
exact actors the gate exists to constrain. `bypass_actors` stays `[]`.

Instead all three workflows call `scripts/ci/push_prevalidated_main.sh`:

```
commit locally
  -> push exact SHA to bot/<label>-<run_id>
  -> workflow_dispatch quality-js.yml --ref that branch
  -> wait for the run whose head_sha == that exact SHA
  -> assert EACH required check name is success on that SHA
  -> push the same SHA to main
  -> delete the temp branch
```

GitHub accepts the final push because the commit already carries passing checks.
If `main` moved while waiting, the helper rebases and **revalidates** — check
results never carry across SHAs. It never force-pushes `main`.

`quality-js.yml` therefore needs its `workflow_dispatch` trigger. That is the
mechanism, not a convenience: a push made with `GITHUB_TOKEN` does not trigger a
workflow, but `workflow_dispatch` invoked with `GITHUB_TOKEN` does. Remove that
trigger and all three bots break.

So the invariant now holds in both directions:

> humans don't bypass the gate, bots don't bypass the gate, and automation still works.

**Do not add a bypass actor to "fix" a failing bot.** A failing bot means its
commit did not pass the gate — which is the gate working.

### Proof the gate binds (run 2026-08-11)

A throwaway PR with one deliberately over-threshold function produced
`ESLint complexity: fail` → PR state `MERGEABLE / BLOCKED` → `gh pr merge`
refused with *"the base branch policy prohibits the merge"*, offering `--admin`
as the only override. Red check now blocks a merge rather than merely displaying
red. Probe branch and PR deleted; `main` never received the file.

### Why the path filters had to go first

`quality-js.yml` previously had `paths:` filters. A required status check that is
skipped by a path filter never reports a conclusion — GitHub shows it as
*"Expected — waiting for status"* and the PR can never merge. PR #235 removed the
filters for this reason. **Do not re-add them while these checks are required.**

### Check the context names still match

The `context` values must equal the job `name:` fields in `quality-js.yml`
(`ESLint complexity`, `Remotion typecheck`). Renaming a job without updating this
file leaves a required check that never reports — the same deadlock.
