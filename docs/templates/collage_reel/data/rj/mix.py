"""Mixa a narração (seg/*.wav nos tempos do timeline.json) + efeitos (sfx.json: [[arquivo, início_s, ganho]]) em narracao.mp3."""
import json, subprocess, os
D = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(f'{D}/timeline.json')); DUR = TL[-1]['e']
SFX = json.load(open(f'{D}/sfx.json')) if os.path.exists(f'{D}/sfx.json') else []
ins = []; flt = []; n = 0
for o in TL:
    ins += ['-i', f"{D}/seg/{o['id']}.wav"]; ms = int(o['vstart']*1000)
    flt.append(f"[{n}:a]aresample=48000,adelay={ms}|{ms},apad[a{n}]"); n += 1
for f, start, gain in SFX:
    ins += ['-i', f'{D}/{f}']; ms = int(start*1000)
    flt.append(f"[{n}:a]aresample=48000,volume={gain},adelay={ms}|{ms},apad[a{n}]"); n += 1
mix = ''.join(f'[a{i}]' for i in range(n)) + f"amix=inputs={n}:normalize=0,atrim=0:{DUR:.2f}[out]"
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(flt) + ';' + mix, '-map', '[out]', '-ac', '1', '-b:a', '96k', f'{D}/narracao.mp3'], check=True)
print('narracao.mp3', round(DUR, 2), 'efeitos:', len(SFX))
