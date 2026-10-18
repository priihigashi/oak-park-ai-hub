"""Baixa séries do Atlas da Violência (Ipea) por UF.
Uso: python3 atlas_fetch.py <pasta_do_reel> <serie_id> ...  (grava atlas_<id>.json)
Descobre o endpoint lendo o JS do próprio site (o caminho da API muda entre versões)."""
import json, re, sys, urllib.request
D = sys.argv[1]; UA = {'User-Agent': 'Mozilla/5.0 tentandochegaratevoce-reel'}
B = 'https://www.ipea.gov.br'
def get(u, t=60): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t).read().decode('utf-8', 'ignore')
html = get(B + '/atlasviolencia/dados-series/20')
js = re.findall(r'src="([^"]+\.js[^"]*)"', html)
pats = set()
for s in js:
    u = s if s.startswith('http') else B + (s if s.startswith('/') else '/atlasviolencia/' + s)
    try:
        c = get(u)
        for m in re.findall(r'["\'`]([^"\'`]*api[^"\'`]{0,80})["\'`]', c): pats.add(m)
    except Exception as e: print('js falhou', u, e)
print('JS:', js); print('PADROES API:'); [print(' ', p) for p in sorted(pats)[:80]]
for sid in sys.argv[2:]:
    for path in (f'/atlasviolencia/api/v1/valores-series/{sid}/3', f'/atlasviolencia/api/v1/valores-series/{sid}/4',
                 f'/atlasviolencia/api/v1/series/{sid}/valores/3', f'/atlasviolencia/api/v1/valores-series/{sid}'):
        try:
            data = json.loads(get(B + path))
            json.dump(data, open(f'{D}/atlas_{sid}.json', 'w'), ensure_ascii=False); print('ok', path); break
        except Exception as e: print('falhou', path, e)
