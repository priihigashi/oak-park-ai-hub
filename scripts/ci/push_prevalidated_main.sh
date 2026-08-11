#!/usr/bin/env bash
#
# push_prevalidated_main.sh — land an automated commit on a ruleset-protected main
# WITHOUT granting any bypass actor.
#
# WHY THIS EXISTS
# ---------------
# Ruleset 20720805 requires "ESLint complexity" and "Remotion typecheck" on main,
# with bypass_actors: []. Ruleset required-status-checks apply to DIRECT PUSHES,
# not just merges — a bot pushing straight to main is rejected with
# "2 of 2 required status checks are expected".
#
# GitHub does accept a push whose commit ALREADY has the required checks passing.
# So instead of bypassing the gate, bots pass through it:
#
#   commit locally
#     -> push that exact commit to a temporary bot/* branch
#     -> workflow_dispatch quality-js.yml against that branch
#     -> wait for the run, then verify the check runs on the EXACT SHA
#     -> push the same green SHA to main
#     -> delete the temporary branch
#
# workflow_dispatch is required: a push made with GITHUB_TOKEN deliberately does
# NOT trigger another workflow, but workflow_dispatch invoked with GITHUB_TOKEN
# does create a run.
#
# USAGE
#   scripts/ci/push_prevalidated_main.sh <label>
#
#   Call it with the commit ALREADY created on the local checkout of main.
#   <label> is a short slug used in the temp branch name (e.g. "nonnegotiables").
#
# REQUIREMENTS in the calling workflow
#   permissions:
#     contents: write
#     actions:  write        # <- required to dispatch quality-js.yml
#   env:
#     GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
#
# EXIT CODES
#   0  commit is on main (or there was nothing to push)
#   1  validation failed, timed out, or the push was rejected — CALLER MUST FAIL
#
set -euo pipefail

LABEL="${1:?usage: push_prevalidated_main.sh <label>}"
REPO="${GITHUB_REPOSITORY:-priihigashi/oak-park-ai-hub}"
RUN_ID="${GITHUB_RUN_ID:-manual$$}"
GATE_WORKFLOW="quality-js.yml"
REQUIRED_CHECKS=("ESLint complexity" "Remotion typecheck")
POLL_SECONDS="${POLL_SECONDS:-15}"
MAX_WAIT_SECONDS="${MAX_WAIT_SECONDS:-900}"   # 15 min; the gate normally runs in ~25s
MAX_REBASE_ATTEMPTS=2

BOT_BRANCH="bot/${LABEL}-${RUN_ID}"

log()  { printf '[prevalidated-push] %s\n' "$*"; }
fail() { printf '[prevalidated-push] ERROR: %s\n' "$*" >&2; exit 1; }

cleanup() {
  # Best-effort delete of the temp ref. Never mask the real exit code.
  git push origin --delete "$BOT_BRANCH" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# --- 0. Is there anything to do? --------------------------------------------
git fetch origin main --quiet
LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(git rev-parse origin/main)"

if [ "$LOCAL_SHA" = "$REMOTE_SHA" ]; then
  log "HEAD already matches origin/main — nothing to push."
  exit 0
fi

if ! git merge-base --is-ancestor "$REMOTE_SHA" "$LOCAL_SHA"; then
  fail "HEAD is not a descendant of origin/main. Rebase before calling this."
fi

# --- validate one SHA through the gate --------------------------------------
validate_sha() {
  local sha="$1"

  log "pushing $sha to $BOT_BRANCH for validation"
  git push --force origin "${sha}:refs/heads/${BOT_BRANCH}" \
    || fail "could not push temporary branch $BOT_BRANCH"

  log "dispatching $GATE_WORKFLOW against $BOT_BRANCH"
  gh workflow run "$GATE_WORKFLOW" --repo "$REPO" --ref "$BOT_BRANCH" \
    || fail "could not dispatch $GATE_WORKFLOW (is 'actions: write' set?)"

  local waited=0
  local conclusion=""
  while [ "$waited" -lt "$MAX_WAIT_SECONDS" ]; do
    sleep "$POLL_SECONDS"
    waited=$(( waited + POLL_SECONDS ))

    # Only consider runs whose head_sha is EXACTLY the commit we are landing.
    # Results from any other SHA are worthless here.
    conclusion="$(gh run list --repo "$REPO" --workflow "$GATE_WORKFLOW" \
        --branch "$BOT_BRANCH" --limit 10 \
        --json headSha,status,conclusion \
        --jq "[.[] | select(.headSha==\"$sha\" and .status==\"completed\")][0].conclusion // \"\"")"

    [ -n "$conclusion" ] && break
    log "  waiting for gate run on $sha (${waited}s)"
  done

  [ -n "$conclusion" ] || fail "gate did not complete within ${MAX_WAIT_SECONDS}s for $sha"
  [ "$conclusion" = "success" ] || fail "gate concluded '$conclusion' for $sha — refusing to push"

  # Belt and braces: assert each REQUIRED check individually, by name, on this SHA.
  # A green workflow run is not the same claim as "every required context passed".
  local checks
  checks="$(gh api "repos/${REPO}/commits/${sha}/check-runs" --paginate \
      --jq '.check_runs[] | "\(.name)=\(.conclusion)"')"

  local c
  for c in "${REQUIRED_CHECKS[@]}"; do
    if ! grep -Fxq "${c}=success" <<<"$checks"; then
      log "check runs present on $sha:"
      printf '  %s\n' $checks
      fail "required check '$c' is not success on $sha"
    fi
    log "  verified: $c = success on $sha"
  done
}

# --- 1..N. validate, then push; rebase and revalidate if main moved ----------
attempt=1
while [ "$attempt" -le "$MAX_REBASE_ATTEMPTS" ]; do
  SHA="$(git rev-parse HEAD)"
  validate_sha "$SHA"

  log "pushing validated $SHA to main (attempt $attempt)"
  if git push origin "HEAD:main"; then
    log "SUCCESS — $SHA is on main, validated by the same gate humans face."
    exit 0
  fi

  log "push rejected — main likely moved. Rebasing and revalidating the NEW sha."
  log "(check results do not carry across SHAs, so this must re-run the gate.)"
  git fetch origin main --quiet
  git rebase origin/main || fail "rebase onto origin/main failed — manual intervention needed"
  attempt=$(( attempt + 1 ))
done

fail "could not land commit on main after ${MAX_REBASE_ATTEMPTS} attempts"
