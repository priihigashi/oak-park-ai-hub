"""Shared post-transcription routing contract; no network, billing or publication.

Location IDs remain in routing.py. This module describes isolated downstream
jobs, not another capture pipeline. Legacy callers are intentionally unchanged
until their adapters pass the acceptance matrix in docs/CONTENT_ROUTING.md.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Callable, Mapping, Sequence

from routing import ROUTES

POLICY_VERSION = 1


class RoutingError(ValueError):
    """An ambiguous or invalid route must not fall through into another niche."""


@dataclass(frozen=True)
class Profile:
    family: str
    primary_language: str | None
    default_format: str
    formats: tuple[str, ...]
    skills: tuple[str, ...]
    required_gates: tuple[str, ...]
    editorial: str


_NEWS_GATES = ('claim_evidence', 'dates_and_jurisdiction', 'source_media_provenance',
               'story_coherence', 'visual_readability', 'owner_review')
_NEWS_SKILLS = ('transcribe-comment-create-print', 'transcribe-comment-create')
PROFILES = {
    'brazil': Profile('news', 'pt-BR', 'print', ('print', 'carousel', 'reel'), _NEWS_SKILLS,
        _NEWS_GATES, 'Brazil-audience editorial profile; verify claims before verdicts. '
        'The subject may be another country. Translation must not rewrite the facts.'),
    'usa': Profile('news', 'en-US', 'print', ('print', 'carousel', 'reel'), _NEWS_SKILLS,
        _NEWS_GATES, 'USA-audience editorial profile; verify claims before verdicts. '
        'Do not inherit Brazil-only institutions, outlets or Portuguese-primary layout.'),
    'opc': Profile('construction', 'en-US', 'carousel', ('print', 'carousel', 'reel'),
        ('opc-transcribe-create-print', 'opc-carousel-creator', 'opc-carousel-reviewer', 'opc-reels'),
        ('material_or_code_evidence', 'opc_brand', 'real_project_identity',
         'ai_disclosure', 'visual_readability', 'owner_review'),
        'Original homeowner education or verified project proof, not a newsroom rebuttal. '
        'Visual-first and short copy. AI illustrations are not evidence of completed work. '
        'Use the selected registered format; private research need not fill public slides.'),
    'ugc': Profile('creator', None, 'reel', ('carousel', 'reel', 'storyboard'),
        ('content-chief',),
        ('creator_brief', 'product_or_place_identity', 'first_person_evidence',
         'media_rights_and_consent', 'disclosures', 'visual_readability', 'owner_review'),
        'Creator-led content, not news or OPC branding. Select travel, product or movement '
        'from the actual brief and footage. Never invent a purchase, visit, personal use '
        'or testimonial. Travel keeps real ambient audio and the creator\'s actual opinions.'),
    'stocks': Profile('markets', None, 'carousel', ('carousel', 'reel', 'research'),
        ('content-chief',), ('as_of_time', 'market_evidence', 'risk_context', 'owner_review'),
        'Dated market evidence and uncertainty, not contractor copy or promised returns.'),
    'higashi': Profile('real_estate', 'pt-BR', 'carousel', ('carousel', 'reel'),
        ('content-chief',), ('property_identity', 'listing_evidence', 'brand_brief', 'owner_review'),
        'Real-estate brand and actual property facts; Portuguese does not make this Brazil News.'),
    'book': Profile('long_form', None, 'research', ('research', 'chapter'),
        (), ('source_provenance', 'chapter_scope', 'owner_review'),
        'Source-backed long-form research; do not force a carousel or a news publishing destination.'),
    'ai': Profile('ai_content', None, 'storyboard', ('carousel', 'reel', 'storyboard'),
        ('ai-generation',), ('model_availability', 'generation_rights', 'asset_provenance', 'owner_review'),
        'Use the supplied creative brief and disclosed synthetic assets; do not invent job proof.'),
}
_ALIASES = {'news:brazil': 'brazil', 'news_brazil': 'brazil', 'brasil': 'brazil',
            'news:usa': 'usa', 'news_usa': 'usa'}
_GROUPS = {'news:both': ('brazil', 'usa'), 'news_both': ('brazil', 'usa')}
_FORMAT_ALIASES = {'short': 'reel', 'reels': 'reel'}


@dataclass(frozen=True)
class Capture:
    capture_id: str
    source_ref: str
    text: str
    source_language: str | None = None
    kind: str = 'transcript'

    def __post_init__(self) -> None:
        if not isinstance(self.capture_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,119}', self.capture_id):
            raise RoutingError('A stable, path-safe capture_id is required')
        if not isinstance(self.source_ref, str) or not self.source_ref.strip():
            raise RoutingError('Source reference is required')
        if not isinstance(self.text, str) or not self.text.strip():
            raise RoutingError('Empty source content cannot create downstream jobs')
        if self.kind not in ('transcript', 'visual_description'):
            raise RoutingError('An AI brief is not a transcript')
        if any(marker in self.text for marker in ('[TRANSCRIPT_UNAVAILABLE]', '[MEDIA RETRIEVAL BLOCKED]')):
            raise RoutingError('Unavailable-source placeholders cannot create jobs')

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode('utf-8')).hexdigest()


def select_routes(selection: str | Sequence[str]) -> tuple[str, ...]:
    """Structured selection, not a keyword guess from source text or language.

    Bare 'news' is ambiguous here. The older routing.py alias is preserved for
    backward compatibility, but new entrypoints must select Brazil/USA/both.
    """
    tokens = selection.split(',') if isinstance(selection, str) else list(selection)
    if not tokens or any(not isinstance(x, str) or not x.strip() for x in tokens):
        raise RoutingError('Select a destination; no implicit Brazil or OPC default')
    selected = []
    for token in tokens:
        key = token.strip().casefold()
        expanded = _GROUPS.get(key, (_ALIASES.get(key, key),))
        for route in expanded:
            if route not in ROUTES or route not in PROFILES:
                raise RoutingError('Unsupported or ambiguous destination: ' + key)
            if route not in selected:
                selected.append(route)
    return tuple(selected)


def _options(route: str, supplied: Mapping[str, Any]) -> dict[str, Any]:
    unknown = set(supplied) - {'format', 'output_language', 'subtype'}
    if unknown:
        raise RoutingError('Unknown per-route options: ' + ', '.join(sorted(unknown)))
    profile = PROFILES[route]
    requested_format = supplied.get('format', profile.default_format)
    output_format = _FORMAT_ALIASES.get(requested_format, requested_format)
    if output_format not in profile.formats:
        raise RoutingError(f'{route} does not support requested format {output_format}')
    language = supplied.get('output_language') or profile.primary_language
    if language is not None and (not isinstance(language, str) or not re.fullmatch(r'[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*', language)):
        raise RoutingError('Invalid output language')
    subtype = supplied.get('subtype')
    if subtype is not None and (route != 'ugc' or subtype not in ('product', 'travel', 'movement')):
        raise RoutingError('Unsupported subtype for selected route')
    return {'format': output_format, 'output_language': language, 'subtype': subtype}


def _job(capture: Capture, route: str, options: Mapping[str, Any]) -> dict[str, Any]:
    profile, destination = PROFILES[route], ROUTES[route]
    resolved = _options(route, options)
    identity = [POLICY_VERSION, capture.capture_id, capture.source_ref, capture.sha256,
                capture.kind, route, resolved]
    job_key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode('utf-8')).hexdigest()
    skills = list(profile.skills)
    if resolved['subtype'] == 'travel':
        skills.append('travel-ugc')
    return {
        'job_key': job_key, 'capture_id': capture.capture_id, 'source_sha256': capture.sha256,
        'route': route, 'family': profile.family, **resolved,
        'source_language': capture.source_language, 'source_kind': capture.kind,
        'skills': skills, 'editorial': profile.editorial,
        'required_gates': list(profile.required_gates),
        'destination': {k: destination.get(k, '') for k in
                        ('drive_id', 'capture_folder_id', 'carousel_folder_id', 'reels_folder_id',
                         'content_control_id', 'content_control_tab')},
        'status': 'ROUTED_NOT_BUILT', 'approved': False, 'publish_allowed': False,
    }


def build_route_plan(capture: Capture, selection: str | Sequence[str],
                     options: Mapping[str, Mapping[str, Any]] | None = None) -> dict[str, Any]:
    routes = select_routes(selection)
    options = options or {}
    if set(options) - set(routes):
        raise RoutingError('Options name an unselected/non-canonical destination')
    jobs = [_job(capture, route, options.get(route, {})) for route in routes]
    return {'policy_version': POLICY_VERSION, 'capture_id': capture.capture_id,
            'source_sha256': capture.sha256, 'jobs': jobs, 'approved': False,
            'status': 'ROUTED_NOT_BUILT', 'shared_capture_count': 1}


def dispatch_after_transcription(capture: Capture, selection: str | Sequence[str],
                                 handlers: Mapping[str, Callable],
                                 options: Mapping[str, Mapping[str, Any]] | None = None) -> dict[str, Any]:
    """Deliver one immutable capture to distinct adapters, with isolated job data.

    The caller must provide reviewed adapters and persist/reserve job_key before
    any paid work. A successful callback is only a handoff, never evidence of a
    finished post, paid model success, owner approval or live publication.
    """
    plan = build_route_plan(capture, selection, options)
    missing = [j['route'] for j in plan['jobs'] if not callable(handlers.get(j['route']))]
    if missing:
        raise RoutingError('No registered adapter for: ' + ', '.join(missing))
    receipts = []
    for job in plan['jobs']:
        record = {'route': job['route'], 'job_key': job['job_key'], 'approved': False}
        try:
            handlers[job['route']](capture, deepcopy(job))
            record['status'] = 'HANDOFF_RETURNED_NOT_VERIFIED'
        except Exception as exc:
            record.update(status='HANDOFF_FAILED', error_type=type(exc).__name__)
        receipts.append(record)
    return {**plan, 'handoffs': receipts, 'status': 'NOT_BUILT_BY_ROUTER'}
