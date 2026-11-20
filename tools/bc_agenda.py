import json, os, time
from playwright.sync_api import sync_playwright
os.makedirs('bc_out', exist_ok=True)
caps = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    def on_resp(r):
        if '/api/' in r.url or 'agenda' in r.url.lower():
            try:
                body = r.text()
            except Exception:
                body = ''
            caps.append({'url': r.url, 'status': r.status, 'body': body[:300000]})
    pg.on('response', on_resp)
    for u in ['https://www.bcb.gov.br/c/agendadiretoria/', 'https://www.bcb.gov.br/acessoinformacao/agendadiretoria#!/c/agendadiretoria/']:
        try:
            pg.goto(u, wait_until='networkidle', timeout=90000)
        except Exception as e:
            print('goto', u, e)
        time.sleep(6)
        open('bc_out/page_' + str(len(caps)) + '.txt', 'w').write(pg.inner_text('body')[:50000])
        # clicar no primeiro link que pareca diretor/presidente
        for txt in ['Presidente', 'Gabriel', 'Diretor']:
            try:
                pg.get_by_text(txt).first.click(timeout=5000)
                time.sleep(5)
                break
            except Exception:
                pass
        open('bc_out/page2_' + str(len(caps)) + '.txt', 'w').write(pg.inner_text('body')[:50000])
    json.dump(caps, open('bc_out/probe2.json', 'w'), ensure_ascii=False)
    b.close()
print(len(caps), [c['url'] for c in caps][:60])
