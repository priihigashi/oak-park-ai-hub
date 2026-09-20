"""Bounded editorial repair: preserve evidence and review again, never force pass."""
from __future__ import annotations
import json
import re
from pathlib import Path
from opc_contract import GateError, check_copy, words

REVIEW = '''Review this OPC draft against the ACTUAL source excerpts, not the researcher's
summaries. Check all factual claims, English, coherent sequence, each image-to-copy mapping,
and source_ids. Generic instructions to inspect one's own sample are editorial advice;
precise time periods, technical claims or performance claims need direct evidence.
No invented sponsor, #ad, purchase, personal experience, project, price or competitor names.
Return {"passed":true|false,"issues":["specific actionable problems"],"english":true|false}.
Do not invent a problem or approve unsupported claims. This is a same-provider review,
not an independent Council or owner approval.'''

REPAIR = '''Repair the supplied OPC draft using the actual excerpts and review issues.
Return the SAME JSON schema with title, caption, hashtags, slides, visuals. Do not rewrite
or invent source evidence. Use 5-6 slides. Headlines 3-7 words; total headline+body <=25
words and body <=150 characters. Each middle slide needs the exact supporting source_ids.
Keep one simple useful point per slide. Remove technical jargon rather than expanding it.
Remove unsupported numbers, time periods, absolutes, guarantees and invented sponsorship.
The audience needs a practical homeowner tip, not a scientific lecture or debunk.
Use exactly four sequential visuals A1-A4, every one directly relevant to its assigned
slides. Prefer room, detail, material sample and practical sample-testing scenes.
No compass diagrams, charts, text, logos, labels, brand-specific shade codes, exact color
match promises, or unverified before/after. All images are conceptual illustrations,
not experiments or OPC projects. Close with a useful save/decision takeaway.
The caption must not include #ad or imply sponsorship without explicit verified support.'''


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def accepted(result: dict) -> bool:
    return result.get('passed') is True and result.get('english') is True and result.get('issues') == []


def copy_checks(draft: dict) -> list[str]:
    errors = [error for i, c in enumerate(draft.get('slides', []), 1) for error in check_copy(c, i)]
    if not 5 <= len(draft.get('slides', [])) <= 8:
        errors.append('Invalid number of cards')
    if re.search(r'(?i)(?:#ad\b|\bsponsored\b|\bpaid partnership\b)', str(draft.get('caption', ''))):
        errors.append('Unverified sponsorship in caption')
    return errors


def review_draft(model, draft: dict, evidence: list, aliases: list, root: Path) -> dict:
    result = model.ask(REVIEW, {'draft': draft, 'evidence': evidence, 'banned_names': aliases})
    result['issues'] = list(result.get('issues') or []) + copy_checks(draft)
    if result['issues']:
        result['passed'] = False
    write(root / f'editorial-attempt-{model.calls:02d}.json', result)
    return result


def repair_after_review(model, draft: dict, evidence: list, aliases: list, root: Path, failed: dict) -> tuple[dict, dict]:
    if accepted(failed) or model.calls + 2 > model.max_calls:
        raise GateError('Repair requires a failed review and two remaining authorized calls')
    write(root / 'feed-before-editorial-repair.json', draft)
    fixed = model.ask(REPAIR, {'draft': draft, 'issues': failed.get('issues', []),
                             'evidence': evidence, 'banned_names': aliases})
    write(root / 'feed-draft.json', fixed)
    result = review_draft(model, fixed, evidence, aliases, root)
    if not accepted(result):
        raise GateError('Bounded editorial repair did not pass; no additional paid retry')
    return fixed, certificate(model, repaired=True)


def certificate(model, repaired: bool) -> dict:
    return {'passed': True, 'english': True, 'provider': model.engine, 'model': model.model,
            'independent_council': False, 'repaired': repaired,
            'method': 'separate source review request; owner approval still required'}


def review_or_repair(model, draft: dict, evidence: list, aliases: list, root: Path) -> tuple[dict, dict]:
    result = review_draft(model, draft, evidence, aliases, root)
    if accepted(result):
        return draft, certificate(model, repaired=False)
    return repair_after_review(model, draft, evidence, aliases, root, result)
