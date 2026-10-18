"""Baixa candidatas de imagem do Wikimedia Commons com licença registrada.
Uso: python3 commons_fetch.py <pasta_do_reel>   (lê images.json: {chave: "busca" ou ["File:Nome.jpg", ...]})
Grava cands/<chave>_<n>.jpg (1600 px de largura) e cands/credits.json (autor, licença, link)."""
import json, os, re, sys, time, urllib.parse, urllib.request

D = sys.argv[1]; N = int(os.environ.get('PER', '3'))
Q = json.load(open(f'{D}/images.json'))
os.makedirs(f'{D}/cands', exist_ok=True)
UA = {'User-Agent': 'tentandochegaratevoce-reel/1.0 (priihigashi/oak-park-ai-hub)'}
API = 'https://commons.wikimedia.org/w/api.php?'

def get(params):
    req = urllib.request.Request(API + urllib.parse.urlencode(params), headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=40))

def strip(h): return re.sub(r'<[^>]+>', '', h or '').strip()

CR = {}
for key, q in Q.items():
    if isinstance(q, list):
        titles = q
    else:
        r = get(dict(action='query', format='json', list='search', srnamespace=6, srlimit=12,
                     srsearch=f'{q} filetype:bitmap'))
        titles = [x['title'] for x in r['query']['search'] if re.search(r'\.(jpe?g|png)$', x['title'], re.I)]
    n = 0
    for t in titles:
        if n >= N: break
        try:
            r = get(dict(action='query', format='json', titles=t, prop='imageinfo',
                         iiprop='url|extmetadata|size', iiurlwidth=1600))
            p = next(iter(r['query']['pages'].values())); ii = p['imageinfo'][0]
            if ii.get('width', 0) < 1000: continue
            m = ii.get('extmetadata', {})
            lic = strip(m.get('LicenseShortName', {}).get('value'))
            if not re.search(r'CC|Public domain|PD', lic, re.I): continue
            url = ii.get('thumburl') or ii['url']
            fn = f'{key}_{n}.jpg'
            req = urllib.request.Request(url, headers=UA)
            open(f'{D}/cands/{fn}', 'wb').write(urllib.request.urlopen(req, timeout=60).read())
            CR[fn] = dict(title=t, license=lic, artist=strip(m.get('Artist', {}).get('value'))[:120],
                          credit=strip(m.get('Credit', {}).get('value'))[:160],
                          page=ii.get('descriptionurl'))
            print(fn, '|', lic, '|', t); n += 1
            time.sleep(0.4)
        except Exception as e:
            print('skip', t, e)
    if n == 0: print('NADA PARA', key, q)
json.dump(CR, open(f'{D}/cands/credits.json', 'w'), ensure_ascii=False, indent=1)
