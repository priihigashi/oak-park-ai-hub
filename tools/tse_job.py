import json, os, urllib.request
os.makedirs("out/tse", exist_ok=True)
H = {"User-Agent": "Mozilla/5.0"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=30).read()
B = "https://resultados.tse.jus.br/oficial/ele2026"
UFS = "br ac al ap am ba ce df es go ma mt ms mg pa pb pr pe pi rj rn rs ro rr sc sp se to".split()
log = []; ok = {}
pats = ["{cd}/dados-simplificados/{uf}/{uf}-c0001-e{e}-r.json", "{cd}/dados/{uf}/{uf}-c0001-e{e}-v.json", "{cd}/dados/{uf}/{uf}-c0001-e{e}-r.json", "{cd}/dados/{uf}/{uf}-c0001-e{e}-u.json", "{cd}/dados/{uf}/{uf}-e{e}-v.json"]
good = None
for p in pats:
    u = B + "/" + p.format(cd=6258, uf="br", e="006258")
    try: get(u); good = p; log.append("OK " + p); break
    except Exception as ex: log.append(f"{p} {ex}")
if good:
    for cd in (6257, 6258):
        for uf in UFS:
            try:
                d = get(B + "/" + good.format(cd=cd, uf=uf, e=f"{cd:06d}"))
                open(f"out/tse/{cd}_{uf}.json", "wb").write(d)
            except Exception as ex: log.append(f"{cd} {uf} {ex}")
open("out/tse/log.txt","w").write("\n".join(log))
