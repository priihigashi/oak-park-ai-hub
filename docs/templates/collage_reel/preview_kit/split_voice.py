"""Corta uma ou mais narrações longas (ElevenLabs, 1 take) em tts/<cena>.mp3 + words.json, alinhando o texto do roteiro
com os tempos por palavra do faster-whisper. Uso: python3 split_voice.py <pasta_do_reel> parte1.mp3:s01,s02,... parte2.mp3:s09,...
words.json fica com a GRAFIA do roteiro (legenda certa) e os tempos da voz."""
import json, re, subprocess, sys, unicodedata, difflib, os
from faster_whisper import WhisperModel
D = sys.argv[1]; S = json.load(open(f'{D}/script.json'))
def norm(w): return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', w.lower()).encode('ascii', 'ignore').decode())
m = WhisperModel(os.environ.get('WM', 'small'), device='cpu', compute_type='int8')
W = json.load(open(f'{D}/words.json')) if os.path.exists(f'{D}/words.json') else {}
os.makedirs(f'{D}/tts', exist_ok=True)
for arg in sys.argv[2:]:
    f, scenes = arg.split(':'); scenes = scenes.split(',')
    segs, _ = m.transcribe(f, language='pt', word_timestamps=True, beam_size=5)
    hw = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
    sw = []  # (scene, word)
    for k in scenes: sw += [(k, w) for w in S[k].split()]
    a = [norm(w) for _, w in sw]; b = [norm(w) for w, _, _ in hw]
    t = [None] * len(sw)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for i in range(blk.size): t[blk.a + i] = (hw[blk.b + i][1], hw[blk.b + i][2])
    # interpola os que não casaram
    for i in range(len(t)):
        if t[i] is None:
            p = next((t[j] for j in range(i - 1, -1, -1) if t[j]), (0, 0)); n = next((t[j] for j in range(i + 1, len(t)) if t[j]), (p[1] + .3, p[1] + .6))
            t[i] = (p[1], max(p[1] + .05, n[0]))
    print(f, 'casadas', sum(1 for x in t if x), '/', len(t))
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))
    idx = {k: [i for i, (kk, _) in enumerate(sw) if kk == k] for k in scenes}
    for n, k in enumerate(scenes):
        first, last = idx[k][0], idx[k][-1]
        a0 = 0 if n == 0 else (t[idx[scenes[n - 1]][-1]][1] + t[first][0]) / 2
        a1 = dur if n == len(scenes) - 1 else (t[last][1] + t[idx[scenes[n + 1]][0]][0]) / 2
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-ss', f'{a0:.3f}', '-to', f'{a1:.3f}', '-c:a', 'libmp3lame', '-q:a', '2', f'{D}/tts/{k}.mp3'], check=True)
        W[k] = [[sw[i][1], round(t[i][0] - a0, 4), round(max(.05, t[i][1] - t[i][0]), 4)] for i in idx[k]]
json.dump(W, open(f'{D}/words.json', 'w'), ensure_ascii=False)
print('ok')
