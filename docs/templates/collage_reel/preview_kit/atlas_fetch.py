"""Baixa séries do Atlas da Violência (Ipea) por UF.
Uso: python3 atlas_fetch.py <pasta_do_reel> <serie_id> [<serie_id> ...]   (grava atlas_<id>.json)
Séries úteis: 20 = taxa de homicídios por 100 mil (UF)."""
import json, sys, urllib.request
D = sys.argv[1]
UA = {'User-Agent': 'tentandochegaratevoce-reel/1.0'}
for sid in sys.argv[2:]:
    for url in (f'https://www.ipea.gov.br/atlasviolencia/api/v1/valores-series/{sid}/3',
                f'https://www.ipea.gov.br/atlasviolencia/api/v1/series/{sid}'):
        try:
            data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
            name = 'atlas_%s%s.json' % (sid, '' if 'valores' in url else '_meta')
            json.dump(data, open(f'{D}/{name}', 'w'), ensure_ascii=False)
            print('ok', url, len(data) if isinstance(data, list) else type(data))
        except Exception as e:
            print('falhou', url, e)
