import json, os, urllib.request
os.makedirs("out/tse", exist_ok=True)
H = {"User-Agent": "Mozilla/5.0"}
def get(u):
    return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=30).read())
B = "https://resultados.tse.jus.br/oficial"
log = []
cfg = None
for u in [f"{B}/comum/config/ele-c.json"]:
    try: cfg = get(u); json.dump(cfg, open("out/tse/ele-c.json","w")); log.append("cfg ok")
    except Exception as e: log.append(f"cfg fail {e}")
UFS = "ac al ap am ba ce df es go ma mt ms mg pa pb pr pe pi rj rn rs ro rr sc sp se to".split()
res = {}
if cfg:
    for pl in cfg.get("pl", []):
        for e in pl.get("e", []):
            if str(e.get("cd","")) and "2026" in json.dumps(pl) and e.get("tp") in (1, "1", None) or True:
                pass
    # find presidential elections (cargo 1) for 2026
    els = []
    for pl in cfg.get("pl", []):
        for e in pl.get("e", []):
            els.append((pl.get("cdpr"), pl.get("dt"), e.get("cd"), e.get("t"), e.get("nm")))
    json.dump(els, open("out/tse/els.json","w"), ensure_ascii=False)
    for _, dt, cd, t, nm in els:
        if not str(dt).endswith("2026") and "2026" not in str(dt): continue
        for uf in UFS + ["br"]:
            try:
                d = get(f"{B}/ele2026/{cd}/dados-simplificados/{uf}/{uf}-c0001-e{int(cd):06d}-r.json")
                res.setdefault(str(cd), {})[uf] = {"cand": [(c.get("nm"), c.get("vap")) for c in d.get("cand", [])], "tv": d.get("tv"), "vb": d.get("vb"), "tvn": d.get("tvn"), "a": d.get("a"), "c": d.get("c")}
            except Exception as ex:
                log.append(f"{cd} {uf} {ex}"); 
json.dump(res, open("out/tse/res.json","w"), ensure_ascii=False)
open("out/tse/log.txt","w").write("\n".join(log[:200]))
print(len(res), log[:5])
