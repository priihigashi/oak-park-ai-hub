import json, os, re, time
from playwright.sync_api import sync_playwright
os.makedirs('bc_out', exist_ok=True)
caps = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    def on_resp(r):
        u = r.url
        if '/api/' in u:
            try:
                body = r.text()
            except Exception:
                body = ''
            caps.append({'url': u, 'status': r.status, 'body': body[:200000]})
    pg.on('response', on_resp)
    pg.goto('https://www.bcb.gov.br/acessoinformacao/agendadiretoria', wait_until='networkidle', timeout=90000)
    time.sleep(5)
    json.dump(caps, open('bc_out/probe.json', 'w'), ensure_ascii=False)
    # try to reuse any agenda-like endpoint with date params for Jan-Aug 2026
    agenda = [c['url'] for c in caps if re.search('agenda', c['url'], re.I)]
    out = {}
    if agenda:
        base = agenda[0]
        import datetime as dt
        d = dt.date(2026, 1, 1)
        while d <= dt.date(2026, 8, 31):
            ds = d.isoformat()
            u = re.sub(r'(\d{4}-\d{2}-\d{2})', ds, base, count=1)
            if u == base:
                u = base + ('&' if '?' in base else '?') + 'data=' + ds
            try:
                txt = pg.evaluate('u => fetch(u).then(r => r.text())', u)
            except Exception as e:
                txt = 'ERR ' + str(e)
            out[ds] = {'url': u, 'body': txt[:100000]}
            d += dt.timedelta(days=1)
    json.dump(out, open('bc_out/jan_ago.json', 'w'), ensure_ascii=False)
    b.close()
print(len(caps), [c['url'] for c in caps][:30])
