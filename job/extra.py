import requests, pandas as pd, json
rows = []
for y in range(1994, 2021):
    for a, b in [(f"01/01/{y}", f"30/06/{y}"), (f"01/07/{y}", f"31/12/{y}")]:
        for k in range(3):
            try:
                r = requests.get(f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados?formato=json&dataInicial={a}&dataFinal={b}", timeout=30)
                if r.status_code == 200 and r.text.strip().startswith("["):
                    rows += r.json(); break
                print(y, r.status_code, r.text[:80], flush=True)
            except Exception as e:
                print(y, e, flush=True)
s = pd.Series({pd.to_datetime(x["data"], dayfirst=True): float(x["valor"]) for x in rows}).sort_index()
s.to_csv("out/ptax_hist.csv", header=["v"])
print(len(s), s.index[0], s.index[-1])
