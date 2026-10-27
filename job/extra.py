import requests, pandas as pd
r = requests.get("http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='GM366_ERC366')", timeout=180)
v = r.json()["value"]
s = pd.Series({pd.to_datetime(x["VALDATA"][:10]): x["VALVALOR"] for x in v if x["VALVALOR"] is not None}).sort_index()
s.to_csv("out/ptax_hist.csv", header=["v"])
print(len(s), s.index[0], s.index[-1])
