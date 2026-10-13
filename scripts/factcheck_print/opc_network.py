"""Credential-free public media reads and authentic source screenshots."""
from __future__ import annotations

import ipaddress
import socket
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

from opc_contract import GateError


def public_https(url: str) -> bool:
    try:
        p = urlparse(url)
        if p.scheme != 'https' or not p.hostname or p.username or p.password or p.port not in (None, 443):
            return False
        addresses = socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM)
        return bool(addresses) and all(ipaddress.ip_address(a[4][0]).is_global for a in addresses)
    except (ValueError, OSError):
        return False


def download(url: str, target: Path, limit: int = 25_000_000) -> Path:
    """Validate every redirect; never forward a provider key to media URLs."""
    for _ in range(5):
        if not public_https(url):
            raise GateError('Blocked non-public media URL')
        with requests.get(url, timeout=(15, 60), allow_redirects=False, stream=True) as r:
            if r.status_code in (301, 302, 303, 307, 308):
                url = urljoin(url, r.headers.get('Location', ''))
                continue
            if not r.ok:raise GateError(f'Public media fetch failed HTTP {r.status_code}')
            target.parent.mkdir(parents=True, exist_ok=True)
            size = 0
            with target.open('wb') as f:
                for chunk in r.iter_content(65536):
                    size += len(chunk)
                    if size > limit:
                        raise GateError('Media exceeds download size limit')
                    f.write(chunk)
            if size < 100:
                raise GateError('Empty or invalid media response')
            return target
    raise GateError('Too many media redirects')


def route_public(route) -> None:
    if route.request.resource_type in ('media', 'websocket') or not public_https(route.request.url):
        route.abort()
    else:
        route.continue_()


def screenshot_source(url: str, path: Path) -> dict:
    """No certificate bypass, paywall bypass, or generated article screenshot."""
    from playwright.sync_api import sync_playwright
    if not public_https(url):
        raise GateError('Blocked non-public source URL')
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={'width': 760, 'height': 1500}, device_scale_factor=3)
        page.route('**/*', route_public)
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=45000)
            page.wait_for_selector('h1', state='visible', timeout=12000)
            heading = page.locator('h1').first.inner_text().strip()
            article=page.locator('main,article').first
            body = article.inner_text() if article.count() else page.locator('body').inner_text()
            wall = ('access denied', 'verify you are human', 'just a moment', 'sign in to continue', 'subscribe to continue')
            if len(heading) < 5 or any(x in (heading + body[:300]).lower() for x in wall):
                raise GateError('Source is an access wall, not usable proof')
            for text in ('Accept all', 'Accept All Cookies', 'Accept cookies'):
                button = page.get_by_role('button', name=text, exact=True)
                if button.count() == 1 and button.is_visible():
                    button.click(timeout=2000)
                    break
            page.evaluate("""()=>{document.querySelectorAll('*').forEach(e=>{
              const c=getComputedStyle(e);
              if(c.position==='fixed'||c.position==='sticky'||e.tagName==='IFRAME')e.remove();
              });document.documentElement.style.overflow='auto';document.body.style.overflow='auto';} """)
            page.locator('h1').first.scroll_into_view_if_needed()
            page.screenshot(path=str(path), full_page=False)
            return {'url': url, 'final_url': page.url, 'heading': heading, 'excerpt': body[:7000]}
        finally:
            browser.close()


def screenshot_candidates(candidates: list[dict], observed: set[str], root: Path, key: str) -> tuple[dict, list[dict]]:
    from opc_llm import url_key
    attempts = []
    for source in candidates[:3]:
        if url_key(source.get('url', '')) not in observed:
            attempts.append({'status': 'not_observed_in_search'})
            continue
        path = root / 'resources' / f'proof-{key}.png'
        try:
            shot = screenshot_source(source['url'], path)
            attempts.append({'url': source['url'], 'status': 'captured'})
            return {**source, **shot, 'id': key, 'screenshot': str(path.relative_to(root)), 'observed_in_search': True}, attempts
        except Exception as exc:
            attempts.append({'url': source.get('url'), 'status': 'failed', 'error_type': type(exc).__name__})
    import json
    (root/'resources'/f'proof-attempts-{key}.json').write_text(json.dumps(attempts,indent=2),encoding='utf-8')
    raise GateError(f'No authentic proof screenshot for {key}; output stays blocked')
