import subprocess, sys, os, json, zipfile, urllib.request, io
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'pandas'], check=True)
import pandas as pd
os.makedirs('out', exist_ok=True)
RES = {}
CASES = {'2022': ('13', '22', 'Lula', 'Bolsonaro')}
for ano, (a, b, na, nb) in CASES.items():
    url = f'https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_{ano}_BR.zip'
    try:
        fn = f'v{ano}.zip'
        subprocess.run(['curl', '-sSL', '--retry', '3', '-o', fn, url], check=True)
        z = zipfile.ZipFile(fn)
        names = [n for n in z.namelist() if n.lower().endswith('.csv')]
        parts = []; cols = None
        for n in names:
            for ch in pd.read_csv(z.open(n), sep=';', encoding='latin1', dtype=str, chunksize=1_000_000):
                if cols is None: cols = list(ch.columns)
                ch = ch[(ch['NR_TURNO'] == '2') & (ch['CD_CARGO'] == '1') if 'CD_CARGO' in ch else (ch['NR_TURNO'] == '2')]
                keep = [c for c in ['SG_UF', 'NM_MUNICIPIO', 'NR_ZONA', 'NR_SECAO', 'NR_VOTAVEL', 'QT_VOTOS', 'NM_LOCAL_VOTACAO'] if c in ch.columns]
                parts.append(ch[keep])
        d = pd.concat(parts); d['QT_VOTOS'] = d.QT_VOTOS.astype(int)
        d = d[d.SG_UF != 'ZZ']
        key = [c for c in ['SG_UF', 'NM_MUNICIPIO', 'NR_ZONA', 'NR_SECAO', 'NM_LOCAL_VOTACAO'] if c in d.columns]
        p = d.pivot_table(index=key, columns='NR_VOTAVEL', values='QT_VOTOS', aggfunc='sum', fill_value=0).reset_index()
        for c in (a, b):
            if c not in p: p[c] = 0
        p['tot'] = p[a] + p[b]
        p = p[p.tot > 0]
        za = p[p[a] == 0]; zb = p[p[b] == 0]
        RES[ano] = {'cols': cols, 'secoes': int(len(p)),
            f'zero_{na}': int(len(za)), f'votos_{nb}_nelas': int(za[b].sum()),
            f'zero_{nb}': int(len(zb)), f'votos_{na}_nelas': int(zb[a].sum()),
            f'zero_{na}_uf': za.SG_UF.value_counts().to_dict(), f'zero_{nb}_uf': zb.SG_UF.value_counts().to_dict()}
        za.to_csv(f'out/zero_{na}_{ano}.csv', index=False); zb.to_csv(f'out/zero_{nb}_{ano}.csv', index=False)
    except Exception as e:
        RES[ano] = {'erro': repr(e)}
json.dump(RES, open('out/zerovotos2022.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(RES, ensure_ascii=False)[:3000])
