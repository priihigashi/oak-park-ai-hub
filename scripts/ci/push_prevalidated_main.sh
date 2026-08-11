#!/usr/bin/env bash
#
# push_prevalidated_main.sh — land an automated commit on a ruleset-protected main
# WITHOUT granting any bypass actor.
#
# WHY THIS EXISTS
# ---------------
# Ruleset 20720805 requires "ESLint complexity" and "Remotion typecheck" on main
# with bypass_actors: []. Those checks apply to DIRECT PUSHES, not just merges —
# a bot pushing straight to main is rejected with
# "2 of 2 required status checks are expected".
#
# WHAT DOES NOT WORK (tested 2026-08-11, do not retry)
# ----------------------------------------------------
# "Push the commit to a temp ref, get the checks green on that exact SHA, then
# push the same SHA to main" — the model suggested by GitHub's branch-protection
# troubleshooting docs — DOES NOT work under a ruleset. Verified end to end:
# both required check runs reported `success` on the exact SHA (confirmed via
# /commits/{sha}/check-runs), and the push to main was STILL rejected with
# "2 of 2 required status checks are expected". Ruleset push evaluation does not
# honour pre-existing check runs the way classic branch protection does.
#
# WHAT DOES WORK
# --------------
# A pull request merge. The merge API evaluates the ruleset and permits the merge
# once the required checks pass on the PR head — proven repeatedly today.
# So bots open a PR and merge it:
#
#   commit locally
#     -> push to bot/<label>-<run_id>
#     -> open a PR against main (the `pull_request` trigger runs the gate; no
#        dispatch needed, because the PR event is not the GITHUB_TOKEN-push case)
#     -> wait for BOTH required checks to conclude on the PR head SHA
#     -> merge via the API; delete the branch
#
# The bot therefore faces exactly the gate a human faces. Nobody bypasses it.
#
# USAGE
#   scripts/ci/push_prevalidated_main.sh <label>
#
#   Call it with the commit ALREADY created on the local checkout of main.
#   <label> is a short slug used in the branch name (e.g. "nonnegotiables").
#
# REQUIREMENTS in the calling workflow
#   permissions:
#     contents:      write
#     pull-requests: write     # <- required to open and merge the PR
#   env:
#     GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
#
# EXIT CODES
#   0  commit is on main (or there was nothing to push)
#   1  the gate failed, timed out, or the merge was refused — CALLER MUST FAIL
#
set -euo pipefail

LABEL="${1:?usage: push_prevalidated_main.sh <label>}"
REPO="${GITHUB_REPOSITORY:-priihigashi/oak-park-ai-hub}"
RUN_ID="${GITHUB_RUN_ID:-manual$$}"
REQUIRED_CHECKS=("ESLint complexity" "Remotion typecheck")
POLL_SECONDS="${POLL_SECONDS:-15}"
MAX_WAIT_SECONDS="${MAX_WAIT_SECONDS:-900}"   # gate runs in ~25s; queueing can add minutes

BOT_BRANCH="bot/${LABEL}-${RUN_ID}"
PR_URL=""

log()  { printf '[prevalidated-push] %s\n' "$*"; }
fail() { printf '[prevalidated-push] ERROR: %s\n' "$*" >&2; exit 1; }

cleanup() {
  # Best-effort. Never mask the real exit code.
  if [ -n "$PR_URL" ]; then
    gh pr close "$PR_URL" --repo "$REPO" --delete-branch >/dev/null 2>&1 || true
  else
    git push origin --delete "$BOT_BRANCH" >/dev/null 2>&1 || true
  fi
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
  log "HEAD is not a descendant of origin/main — rebasing."
  git rebase origin/main || fail "rebase onto origin/main failed — manual intervention needed"
fi

# --- 1. Push the branch and open the PR -------------------------------------
SHA="$(git rev-parse HEAD)"
log "pushing $SHA to $BOT_BRANCH"
git push --force origin "HEAD:refs/heads/${BOT_BRANCH}" \
  || fail "could not push $BOT_BRANCH"

TITLE="$(git log -1 --pretty=%s)"
log "opening PR for $BOT_BRANCH"
PR_URL="$(gh pr create --repo "$REPO" --base main --head "$BOT_BRANCH" \
    --title "$TITLE" \
    --body "Automated commit from \`${LABEL}\` (run ${RUN_ID}), routed through the quality gate by \`scripts/ci/push_prevalidated_main.sh\`.

main is protected by ruleset 20720805 with \`bypass_actors: []\`, so automation cannot push directly. It opens a PR and faces the same required checks a human does.")" \
  || fail "could not open PR (is 'pull-requests: write' set?)"
log "PR: $PR_URL"

# --- 2. Wait for the required checks on the PR head -------------------------
waited=0
while [ "$waited" -lt "$MAX_WAIT_SECONDS" ]; do
  HEAD_SHA="$(gh pr view "$PR_URL" --repo "$REPO" --json headRefOid --jq .headRefOid)"

  # Assert each required check BY NAME on the exact head SHA. A green run is not
  # the same claim as "every required context passed".
  checks="$(gh api "repos/${REPO}/commits/${HEAD_SHA}/check-runs" --paginate \
      --jq '.check_runs[] | select(.status=="completed") | "\(.name)=\(.conclusion)"' 2>/dev/null || true)"

  all_green=1
  for c in "${REQUIRED_CHECKS[@]}"; do
    grep -Fxq "${c}=success" <<<"$checks" || all_green=0
  done

  if [ "$all_green" -eq 1 ]; then
    for c in "${REQUIRED_CHECKS[@]}"; do log "  verified: $c = success on $HEAD_SHA"; done
    break
  fi

  # Fail fast on a definitive red rather than burning the full timeout.
  if grep -qE '=(failure|timed_out|cancelled)$' <<<"$checks"; then
    log "check runs on $HEAD_SHA:"; printf '  %s\n' $checks
    fail "a required check concluded red — refusing to merge"
  fi

  sleep "$POLL_SECONDS"
  waited=$(( waited + POLL_SECONDS ))
  log "  waiting for the gate on $HEAD_SHA (${waited}s)"
done

[ "$waited" -lt "$MAX_WAIT_SECONDS" ] || fail "gate did not conclude within ${MAX_WAIT_SECONDS}s"

# --- 3. Merge -----------------------------------------------------------------
log "merging $PR_URL"
gh pr merge "$PR_URL" --repo "$REPO" --merge --delete-branch \
  || fail "merge refused — the ruleset rejected it despite green checks"

PR_URL=""   # merged and branch deleted; nothing for cleanup() to close
log "SUCCESS — landed on main through the same gate humans face."
