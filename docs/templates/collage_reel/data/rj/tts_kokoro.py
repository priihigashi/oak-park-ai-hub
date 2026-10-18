"""Voz PROVISÓRIA (Kokoro pf_dora, aberta) — substitui a Thalita/edge-tts, que não é acessível deste ambiente.
Gera tts/<cena>.mp3 + words.json (tempos crus por palavra, no formato do build.py da Bahia).
Cada oração (até a pontuação) é sintetizada separadamente: o início de cada oração é exato; as palavras
dentro dela são distribuídas pelo número de letras."""
import json, re, os, subprocess
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

D = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(f'{D}/script.json'))
K = Kokoro('/home/claude/work/tts_models/kokoro-v1.0.onnx', '/home/claude/work/tts_models/voices-v1.0.bin')
SPEED = 0.88   # aproxima o ritmo cru da Thalita; speeds.json continua valendo por cima
SAY = {'UPPs': 'upepês', 'CPI': 'cepeí', 'GLO': 'gê éle ó', 'Alerj': 'Alérj', 'Witzel': 'Uítzel'}
PAUSE = {',': .16, ':': .22, ';': .22, '.': .34, '?': .38, '!': .34}
os.makedirs(f'{D}/tts', exist_ok=True)

def trim(a, sr, th=.012):
    idx = np.where(np.abs(a) > th)[0]
    if not len(idx): return a
    return a[max(0, idx[0]-int(.02*sr)): idx[-1]+int(.06*sr)]

only = os.environ.get('ONLY')
W = json.load(open(f'{D}/words.json')) if os.path.exists(f'{D}/words.json') and only else {}
for k in sorted(S):
    if only and k not in only.split(','): continue
    toks = S[k].split(); clauses = []; cur = []
    for t in toks:
        cur.append(t)
        if re.search(r'[,.;:?!]$', t): clauses.append(cur); cur = []
    if cur: clauses.append(cur)
    audio = []; t = 0.0; words = []; sr = 24000
    for c in clauses:
        txt = ' '.join(SAY.get(re.sub(r'[,.;:?!]', '', w), w) + (w[-1] if SAY.get(re.sub(r'[,.;:?!]', '', w)) and w[-1] in PAUSE else '') for w in c)
        a, sr = K.create(txt, voice='pf_dora', speed=SPEED, lang='pt-br')
        a = trim(np.asarray(a, np.float32), sr)
        d = len(a)/sr
        L = sum(len(re.sub(r'[^\wÀ-ú]', '', w)) + 1.5 for w in c); acc = 0
        for w in c:
            words.append([w, round(t + .03 + (d - .1)*acc/L, 3)]); acc += len(re.sub(r'[^\wÀ-ú]', '', w)) + 1.5
        p = PAUSE.get(c[-1][-1], .12)
        audio += [a, np.zeros(int(p*sr), np.float32)]; t += d + p
    full = np.concatenate(audio[:-1])
    sf.write(f'{D}/tts/{k}.wav', full, sr)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{D}/tts/{k}.wav', '-b:a', '128k', f'{D}/tts/{k}.mp3'], check=True)
    os.remove(f'{D}/tts/{k}.wav')
    W[k] = words
    print(k, round(len(full)/sr, 2), len(words))
json.dump(W, open(f'{D}/words.json', 'w'), ensure_ascii=False)
