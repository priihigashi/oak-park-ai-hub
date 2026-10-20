"""Voz PROVISÓRIA (Kokoro pf_dora) + TEMPO REAL DE CADA PALAVRA por alinhamento forçado (DTW).
Substitui o tts_kokoro.py (que estimava o início da palavra sintetizando o prefixo à parte: a entonação do
prefixo muda e o erro cresce dentro das frases longas).

Como funciona, por oração (até a pontuação):
  1. sintetiza a oração inteira (é o áudio que vai para o reel, idêntico ao tts_kokoro.py);
  2. sintetiza cada palavra sozinha, com a mesma voz, e cola uma atrás da outra (referência com fronteiras conhecidas);
  3. alinha as duas por DTW sobre MFCC: cada fronteira da referência cai no ponto exato da oração real.
Gera tts/<cena>.mp3 + words.json (mesmo formato de antes; build.py e gen_rj.py não mudam).
Uso: python3 tts_align.py   ·   ONLY=v02,v03 python3 tts_align.py  (só algumas cenas)
Quando a voz final vier do ElevenLabs "with timestamps", troque words.json pelos tempos que ele devolve."""
import json, re, os, subprocess
import numpy as np, soundfile as sf, librosa
from kokoro_onnx import Kokoro

D = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(f'{D}/script.json'))
MD = os.environ.get('KOKORO_DIR', '/home/claude/work/tts_models')
K = Kokoro(f'{MD}/kokoro-v1.0.onnx', f'{MD}/voices-v1.0.bin')
SPEED = 0.88
SAY = {'ONG': 'ônguê', 'UPPs': 'upepês', 'CPI': 'cepeí', 'GLO': 'gê éle ó', 'Alerj': 'Alérj', 'Witzel': 'Uítzel'}
PAUSE = {',': .16, ':': .22, ';': .22, '.': .34, '?': .38, '!': .34}
HOP = 0.01
os.makedirs(f'{D}/tts', exist_ok=True)

def say(w):
    b = re.sub(r'[,.;:?!]', '', w)
    return SAY[b] + (w[-1] if w[-1] in PAUSE else '') if b in SAY else w

def trim(a, sr, th=.012):
    idx = np.where(np.abs(a) > th)[0]
    if not len(idx): return a
    return a[max(0, idx[0]-int(.02*sr)): idx[-1]+int(.06*sr)]

def tts(txt):
    a, sr = K.create(txt, voice='pf_dora', speed=SPEED, lang='pt-br')
    return trim(np.asarray(a, np.float32), sr), sr

def feats(a, sr):
    m = librosa.feature.mfcc(y=a, sr=sr, n_mfcc=20, hop_length=int(HOP*sr), n_fft=int(.025*sr*2))
    m = (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)
    return m

def align(clause_audio, sr, words):
    """devolve o início (s) de cada palavra dentro da oração."""
    if len(words) == 1: return [0.0]
    parts = [tts(say(w).rstrip(',.;:?!'))[0] for w in words]
    bounds = np.cumsum([0] + [len(p)/sr for p in parts])[:-1]       # início de cada palavra na referência
    ref = np.concatenate(parts)
    _, wp = librosa.sequence.dtw(X=feats(ref, sr), Y=feats(clause_audio, sr), metric='cosine')
    wp = wp[::-1]                                                     # pares (quadro ref, quadro real), em ordem
    out = []
    for b in bounds:
        fr = int(round(b / HOP))
        hits = wp[wp[:, 0] == fr][:, 1] if fr else np.array([0])
        if not len(hits): hits = wp[np.argmin(np.abs(wp[:, 0] - fr)), 1:2]
        out.append(float(hits.min()) * HOP)
    for i in range(1, len(out)): out[i] = max(out[i], out[i-1] + .06)   # nunca para trás
    return out

only = os.environ.get('ONLY')
W = json.load(open(f'{D}/words.json')) if os.path.exists(f'{D}/words.json') else {}
for k in sorted(S):
    if only and k not in only.split(','): continue
    toks = S[k].split(); clauses = []; cur = []
    for t in toks:
        cur.append(t)
        if re.search(r'[,.;:?!]$', t): clauses.append(cur); cur = []
    if cur: clauses.append(cur)
    audio = []; t = 0.0; words = []; sr = 24000
    for c in clauses:
        a, sr = tts(' '.join(say(x) for x in c))
        d = len(a)/sr
        for w, st in zip(c, align(a, sr, c)):
            words.append([w, round(t + max(.02, min(st, d - .05)), 3)])
        p = PAUSE.get(c[-1][-1], .12)
        audio += [a, np.zeros(int(p*sr), np.float32)]; t += d + p
    full = np.concatenate(audio[:-1])
    sf.write(f'{D}/tts/{k}.wav', full, sr)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{D}/tts/{k}.wav', '-b:a', '128k', f'{D}/tts/{k}.mp3'], check=True)
    os.remove(f'{D}/tts/{k}.wav')
    W[k] = words
    print(k, round(len(full)/sr, 2), len(words), flush=True)
json.dump(W, open(f'{D}/words.json', 'w'), ensure_ascii=False)
