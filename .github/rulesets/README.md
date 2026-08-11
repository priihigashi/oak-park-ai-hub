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

### The bypass is deliberate — do not remove it

`actor_id: 15368` is the **GitHub Actions** integration. Three workflows commit
directly to `main` using `secrets.GITHUB_TOKEN`, and all three break without this:

- `nonnegotiables.yml` — the nightly 4AM `nonnegotiables-bot` update
- `ads_pulse.yml` — refreshes `docs/dashboard/*.html`
- `ads_approval_watcher.yml` — writes `.github/agent_state/ads_api_approved.json`

Repository admins are **not** given a bypass, on purpose. Multiple agent sessions
act with an admin token; an admin bypass would make the gate toothless for exactly
the actor it exists to constrain. If you are genuinely stuck, set `enforcement` to
`"evaluate"` or `"disabled"` and re-apply, rather than adding an admin bypass.

### Why the path filters had to go first

`quality-js.yml` previously had `paths:` filters. A required status check that is
skipped by a path filter never reports a conclusion — GitHub shows it as
*"Expected — waiting for status"* and the PR can never merge. PR #235 removed the
filters for this reason. **Do not re-add them while these checks are required.**

### Check the context names still match

The `context` values must equal the job `name:` fields in `quality-js.yml`
(`ESLint complexity`, `Remotion typecheck`). Renaming a job without updating this
file leaves a required check that never reports — the same deadlock.
