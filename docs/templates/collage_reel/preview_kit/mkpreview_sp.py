"""Monta a prévia ao vivo do reel de SP (mesmo player do mkpreview.py) + áudio (voz + trilha suave, sem batida).
Uso: python3 mkpreview_sp.py <saida>   (precisa de ../sp.html, ../data/sp/timeline.json, ../data/sp/seg/*.wav e ../assets/sp/*.jpg)"""
import json, os, re, shutil, subprocess, sys, time, wave
import numpy as np
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1]; os.makedirs(f'{OUT}/assets/sp', exist_ok=True)
D = f'{KIT}/data/sp'; SR = 48000
TL = json.load(open(f'{D}/timeline.json')); DUR = TL[-1]['e']; N = int(SR * DUR)

# ---- áudio: voz + pad suave (sem batida), com ducking ----
def rd(f):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', f, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
voice = np.zeros(N, np.float32)
for o in TL:
    v = rd(f"{D}/seg/{o['id']}.wav"); i = int(o['vstart'] * SR); j = min(N, i + len(v)); voice[i:j] += v[:j - i]
voice /= np.max(np.abs(voice)) / 0.9
chords = [[146.83, 174.61, 220.0], [116.54, 146.83, 174.61], [130.81, 164.81, 196.0], [110.0, 138.59, 164.81]]
mus = np.zeros(N, np.float32); seg = 4.0
for k in range(int(DUR / seg) + 1):
    a = int(k * seg * SR); b = min(N, int((k + 1) * seg * SR) + int(.6 * SR))
    if a >= N: break
    tt = np.arange(b - a) / SR; c = chords[k % 4]
    s = sum(np.sin(2*np.pi*f*tt) + .3*np.sin(2*np.pi*2*f*tt + .4) + .15*np.sin(2*np.pi*f*1.003*tt) for f in c) / 3
    e = np.minimum(1, tt / 1.2) * np.minimum(1, (len(tt) / SR - tt) / .6)
    mus[a:b] += (s * e * .08).astype(np.float32)
t = np.arange(N) / SR
mus *= np.minimum(1, t / 2.0).astype(np.float32); mus[-int(2*SR):] *= np.linspace(1, 0, int(2*SR)).astype(np.float32)
env = np.abs(voice); k = int(.15 * SR); env = np.convolve(env, np.ones(k) / k, 'same'); duck = 1 - 0.6 * np.clip(env / 0.05, 0, 1)
mix = voice + mus * duck * 0.8; mix = np.tanh(mix * 1.05); mix /= np.max(np.abs(mix)) / 0.95
wav = f'{OUT}/_mix.wav'
with wave.open(wav, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-b:a', '128k', f'{OUT}/narracao.mp3'], check=True); os.remove(wav)

# ---- página ----
h = open(f'{KIT}/sp.html').read()
style = re.search(r'<style>(.*?)</style>', h, re.S).group(1).replace('html,body{width:1080px;height:1920px;overflow:hidden;background:#050608}', '')
stage = re.search(r'(<div id="stage">.*?</div></div>)\s*<script>', h, re.S).group(1)
refs = set(re.findall(r'assets/[\w/.-]+', h + open(f'{KIT}/fx.css').read() + open(f'{KIT}/preview_kit/style.css').read()))
for r in refs:
    s, d = f'{KIT}/{r}', f'{OUT}/{r}'
    if not os.path.exists(s): print('FALTA', r); continue
    os.makedirs(os.path.dirname(d), exist_ok=True)
    if r.endswith('.jpg'): subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', s, '-vf', 'scale=1080:-2', '-q:v', '5', d])
    else: shutil.copy(s, d)
for f in ['fx.js', 'fx2.js', 'fx.css', 'layout.js', 'fit.js']: shutil.copy(f'{KIT}/{f}', f'{OUT}/{f}')
e = open(f'{KIT}/engine.js').read()
e = e.replace("if(!navigator.webdriver){let t0=performance.now();(function loop(){render(((performance.now()-t0)/1000)%DUR);requestAnimationFrame(loop)})()}",
 "(function loop(){const a=document.getElementById('vo');let T=a?a.currentTime:0;render(Math.min(T,DUR-0.01));if(window.__tick)__tick(T);requestAnimationFrame(loop)})();")
open(f'{OUT}/engine.js', 'w').write(e)
VER = os.environ.get('VER', 'v1')
tpl = open(f'{KIT}/preview_kit/mkpreview.py').read()
page = tpl[tpl.index("page=f'''") + 9: tpl.index("'''\nopen(f'{OUT}/qamiga_preview.html'")]
page = page.replace('{style}', '@@STYLE@@').replace('{stage}', '@@STAGE@@').replace('{dur}', f'{DUR:.2f}')
page = page.replace('{int(__import__("time").time())}', str(int(time.time())))
page = page.replace('{{', '{').replace('}}', '}').replace('@@STYLE@@', style).replace('@@STAGE@@', stage)
page = page.replace('Querida Amiga · Prévia', 'São Paulo · Prévia').replace('Querida amiga · prévia', 'São Paulo: culpa da esquerda? · prévia')
page = page.replace('<small id="ver">versão em edição</small>', f'<small id="ver">{VER}</small>')
page = page.replace('<script src="engine.js"></script><script src="layout.js"></script>', '<script src="engine.js"></script><script src="fit.js"></script><script src="layout.js"></script>')
open(f'{OUT}/index.html', 'w').write(page)
print('ok', round(DUR, 1), 's')
