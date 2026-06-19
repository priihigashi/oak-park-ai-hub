"""
Escalation engine — "call until answered" (RM3, RM10).

Locked policy: Priscila first (3 attempts, 2 min apart); if still unanswered,
escalate to Michael (same retry pattern). Voicemail != answered (RM10). If neither
is reached, the failure behavior fires: notify by SMS + log + leave the guest a
holding message. Honors the kill switch (RM11).

Pure logic with injected side-effects (dialer / sleeper / clock / sms / logger) so it
is fully unit-testable without a live telephony provider.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List

from . import config

# Dialer returns one of these for a single call attempt:
ANSWERED = "answered"     # a human picked up
VOICEMAIL = "voicemail"   # machine / voicemail (NOT counted as answered — RM10)
NO_ANSWER = "no_answer"   # rang out / busy / failed


@dataclass
class EscalationResult:
    reached: str | None              # "priscila" | "michael" | None
    attempts: List[dict] = field(default_factory=list)
    failed_over: bool = False        # True if we moved past the primary
    failure_handled: bool = False    # True if nobody reached and fallback behavior ran
    aborted_kill_switch: bool = False


def _attempt_target(
    target: str,
    dialer: Callable[[str], str],
    sleeper: Callable[[float], None],
    attempts_log: List[dict],
    *,
    max_attempts: int,
    interval: int,
) -> bool:
    """Call one target up to max_attempts, spaced by interval. Return True if a HUMAN answered."""
    for n in range(1, max_attempts + 1):
        outcome = dialer(target)
        attempts_log.append({"target": target, "attempt": n, "outcome": outcome})
        if outcome == ANSWERED:
            return True
        # voicemail and no_answer both mean "not reached"; keep retrying until attempts exhausted
        if n < max_attempts:
            sleeper(interval)
    return False


def run_escalation(
    *,
    is_urgent: bool,
    dialer: Callable[[str], str],
    sleeper: Callable[[float], None] = lambda s: None,
    notify_sms: Callable[[str], None] = lambda msg: None,
    leave_guest_holding: Callable[[], None] = lambda: None,
    logger: Callable[[dict], None] = lambda rec: None,
    kill_switch: Callable[[], bool] = config.kill_switch_active,
    max_attempts: int = config.ESCALATION_MAX_ATTEMPTS,
    interval: int = config.ESCALATION_INTERVAL_SECONDS,
) -> EscalationResult:
    """Execute the locked escalation policy. Only runs for urgent issues."""
    result = EscalationResult(reached=None)

    if kill_switch():
        result.aborted_kill_switch = True
        logger({"event": "escalation_aborted", "reason": "kill_switch"})
        return result

    if not is_urgent:
        # Non-urgent issues are captured as notes, not escalated by phone (RM1/RM5).
        logger({"event": "escalation_skipped", "reason": "not_urgent"})
        return result

    # 1) Priscila first
    if _attempt_target(config.ESCALATION_PRIMARY, dialer, sleeper, result.attempts,
                       max_attempts=max_attempts, interval=interval):
        result.reached = config.ESCALATION_PRIMARY
        logger({"event": "escalation_reached", "target": result.reached, "attempts": result.attempts})
        return result

    # 2) Fall over to Michael — keep the same cadence: wait one interval before the first
    # fallback dial so we don't hammer Michael immediately after Priscila's last ring-out.
    result.failed_over = True
    sleeper(interval)
    if _attempt_target(config.ESCALATION_FALLBACK, dialer, sleeper, result.attempts,
                       max_attempts=max_attempts, interval=interval):
        result.reached = config.ESCALATION_FALLBACK
        logger({"event": "escalation_reached", "target": result.reached, "attempts": result.attempts})
        return result

    # 3) Nobody reached -> failure behavior
    notify_sms("URGENT McFolling guest issue — no one answered the escalation calls.")
    leave_guest_holding()
    result.failure_handled = True
    logger({"event": "escalation_failed", "attempts": result.attempts})
    return result
