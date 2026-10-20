"""Voz provisória grátis (Kokoro, pf_dora) frase a frase: pausas curtas e tempos por palavra.
Gera build/narracao.wav + build/timeline.json [{id,s,e,words:[[palavra, t_relativo_à_cena]]}]."""
import json, re, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
K = Kokoro('/home/claude/work/kmodel/kokoro-v1.0.onnx', '/home/claude/work/kmodel/voices-v1.0.bin')
S = json.load(open('/home/claude/oak-park-ai-hub/docs/templates/collage_reel/data/bahia_sc/script.json'))
SAY = {r'\bPT\b': 'pê tê', r'\bPL\b': 'pê éle', r'\bSC\b': 'Santa Catarina'}
SPEED, SR = 1.25, 24000
GAP = {',': .10, ':': .14, '.': .18, '?': .22}
def trim(a, thr=.01):
    idx = np.where(np.abs(a) > thr)[0]
    return a[max(0, idx[0] - 240): idx[-1] + 480] if len(idx) else a
def weight(w):  # peso ~ sílabas
    return max(1, len(re.findall(r'[aeiouáéíóúâêôãõà]+', w.lower()))) + .3
out, TL, t = [], [], 0.0
for sid, text in S.items():
    phrases = []
    for i, part in enumerate(re.split(r'\[M\]', text)):
        voice = 'pm_alex' if i % 2 else 'pf_dora'
        phrases += [(p.strip(), voice) for p in re.findall(r'[^,.:?]+[,.:?]?', part) if p.strip()]
    s0 = t; words = []
    lead = np.zeros(int(.12 * SR)); out.append(lead); t += .12
    for p, vz in phrases:
        say = p
        for a, b in SAY.items(): say = re.sub(a, b, say)
        a, sr = K.create(say, voice=vz, speed=SPEED, lang='pt-br'); a = trim(a)
        d = len(a) / SR; ws = p.split(); tot = sum(weight(w) for w in ws); acc = 0
        for w in ws:
            words.append([w, round(t - s0 + d * acc / tot, 3)]); acc += weight(w)
        out.append(a); t += d
        g = GAP.get(p[-1], .08); out.append(np.zeros(int(g * SR))); t += g
    tail = 1.2 if sid == list(S)[-1] else .25
    out.append(np.zeros(int(tail * SR))); t += tail
    TL.append(dict(id=sid, s=round(s0, 3), e=round(t, 3), words=words))
sf.write('/home/claude/work/build/narracao.wav', np.concatenate(out), SR)
json.dump(TL, open('/home/claude/work/build/timeline.json', 'w'), ensure_ascii=False)
for o in TL: print(o['id'], round(o['e'] - o['s'], 2))
print('TOTAL', round(t, 2))
