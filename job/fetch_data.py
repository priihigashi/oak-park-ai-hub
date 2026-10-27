import json, os
import pandas as pd, numpy as np, requests

OUT = "out"
os.makedirs(OUT, exist_ok=True)
log = []

ELECTIONS = {
    "1994": "1994-10-03", "1998": "1998-10-04",
    "2002": "2002-10-27", "2006": "2006-10-29", "2010": "2010-10-31",
    "2014": "2014-10-26", "2018": "2018-10-28", "2022": "2022-10-30",
    "2026": "2026-10-25",
}
series = {}

def yf_series(tk):
    import yfinance as yf
    df = yf.download(tk, start="1993-01-01", end="2026-10-28", progress=False, auto_adjust=False)
    s = df["Close"]
    if isinstance(s, pd.DataFrame):
        s = s.iloc[:, 0]
    s = s.dropna()
    s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
    return s

for name, tk in [("ibov", "^BVSP"), ("usdbrl_yf", "BRL=X"), ("sp500", "^GSPC"), ("ewz", "EWZ")]:
    try:
        series[name] = yf_series(tk)
        log.append(f"{name}: {len(series[name])} pts, {series[name].index[0].date()}..{series[name].index[-1].date()}")
    except Exception as e:
        log.append(f"{name} FAIL {e}"); print(log[-1], flush=True)

def sgs(code, y0=1994):
    out = []
    for y in range(y0, 2027, 9):
        a = f"01/01/{y}"; b = f"31/12/{min(y+8, 2026)}"
        r = requests.get(f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json&dataInicial={a}&dataFinal={b}", timeout=40)
        if r.status_code == 200 and r.text.strip().startswith("["):
            out += r.json()
    return pd.Series({pd.to_datetime(x["data"], dayfirst=True): float(x["valor"]) for x in out}).sort_index()

for name, code in [("ptax", 1), ("swap360", 7806), ("swap1800", 7816)]:
    try:
        series[name] = sgs(code)
        log.append(f"{name}: {len(series[name])} pts, {series[name].index[0].date()}..{series[name].index[-1].date()}")
    except Exception as e:
        log.append(f"{name} FAIL {e}"); print(log[-1], flush=True)

try:
    r = requests.get("http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='JPM366_EMBI366')", timeout=120)
    v = r.json()["value"]
    s = pd.Series({pd.to_datetime(x["VALDATA"][:10]): x["VALVALOR"] for x in v if x["VALVALOR"] is not None}).sort_index()
    series["embi"] = s
    log.append(f"embi: {len(s)} pts, {s.index[0].date()}..{s.index[-1].date()}")
except Exception as e:
    log.append(f"embi FAIL {e}")

series = {k: s for k, s in series.items() if len(s) > 10 and isinstance(s.index, pd.DatetimeIndex)}
print("\n".join(log), flush=True)
for k, s in series.items():
    s.to_csv(f"{OUT}/{k}.csv", header=["v"])

def window(s, eday, higher_is_bad):
    e = pd.Timestamp(eday)
    before = s[s.index < e]
    after = s[s.index > e]
    if len(before) == 0 or len(after) == 0:
        return None
    base = float(before.iloc[-1])
    res = {"base": base, "base_date": str(before.index[-1].date())}
    def at(days):
        t = e + pd.Timedelta(days=days)
        a = after[after.index >= t]
        if len(a) == 0:
            return None
        return float(a.iloc[0]), str(a.index[0].date())
    res["d1"] = (float(after.iloc[0]), str(after.index[0].date()))
    for lab, dd in [("w1", 7), ("m1", 30), ("m3", 91), ("m6", 182), ("y1", 365)]:
        res[lab] = at(dd)
    for lab in ["d1", "w1", "m1", "m3", "m6", "y1"]:
        if res[lab]:
            res[lab + "_pct"] = round((res[lab][0] / base - 1) * 100, 2)
    rec = None
    for i, (d, v) in enumerate(after.items()):
        ok = v <= base if higher_is_bad else v >= base
        if ok:
            rec = (str(d.date()), (d - e).days, i + 1)
            break
    res["recover"] = rec
    a3 = after[after.index <= e + pd.Timedelta(days=91)]
    if len(a3):
        w = a3.max() if higher_is_bad else a3.min()
        res["worst3m_pct"] = round((w / base - 1) * 100, 2)
        res["worst3m_date"] = str((a3.idxmax() if higher_is_bad else a3.idxmin()).date())
    for lab, dd in [("pre3m", 91), ("pre1m", 30), ("pre6m", 182)]:
        p = before[before.index <= e - pd.Timedelta(days=dd)]
        if len(p):
            res[lab + "_pct"] = round((base / float(p.iloc[-1]) - 1) * 100, 2)
            res[lab + "_val"] = float(p.iloc[-1])
    return res

summary = {}
bad = {"ibov": False, "sp500": False, "ewz": False, "ptax": True, "usdbrl_yf": True, "embi": True, "swap360": True, "swap1800": True}
for k, s in series.items():
    summary[k] = {}
    for y, d in ELECTIONS.items():
        try:
            summary[k][y] = window(s, d, bad.get(k, False))
        except Exception as ex:
            summary[k][y] = "ERR " + str(ex)

extra = {}
for nm in series:
    try:
        s = series[nm]
        extra[nm + "_2026_path"] = {str(d.date()): float(v) for d, v in s[s.index >= "2026-01-01"].items()}
        last = s.iloc[-1]
        hib = bad.get(nm, False)
        prior = s[(s.index < "2026-10-24") & ((s >= last) if hib else (s <= last))]
        extra[nm + "_last"] = [float(last), str(s.index[-1].date())]
        extra[nm + "_last_time_as_bad"] = str(prior.index[-1].date()) if len(prior) else None
    except Exception as e:
        extra[nm + "_err"] = str(e)

paths = {}
for k in ["ibov", "ptax", "usdbrl_yf", "sp500", "embi", "swap360", "ewz"]:
    if k not in series: continue
    s = series[k]; paths[k] = {}
    for y, d in ELECTIONS.items():
        e = pd.Timestamp(d)
        b = s[s.index < e]
        a = s[s.index > e].iloc[:130]
        if len(b) and len(a):
            base = float(b.iloc[-1])
            paths[k][y] = [round((float(v) / base - 1) * 100, 2) for v in a.values]
json.dump({"log": log, "summary": summary, "extra": extra, "paths": paths}, open(f"{OUT}/market.json", "w"), indent=1, default=str)
print("\n".join(log))
