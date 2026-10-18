"""Monta seg/*.wav + timeline.json a partir de tts/<cena>.mp3 + words.json (tempos crus da voz) + speeds.json.
Uso: python3 build.py   (rodar de novo sempre que trocar a voz; as velocidades por cena vêm de speeds.json)"""
import json,subprocess,re,os
D=os.path.dirname(os.path.abspath(__file__))
W=json.load(open(f'{D}/words.json')); S=json.load(open(f'{D}/script.json')); SP=json.load(open(f'{D}/speeds.json'))['speeds']
norm=lambda w: re.sub(r'[^\wÀ-ú]','',w.lower())
TL=[];t=0
for k in sorted(S):
    sp=SP[k]
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'{D}/tts/{k}.mp3','-filter:a',f'atempo={sp}','-ar','48000',f'{D}/seg/{k}.wav'],check=True)
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{D}/seg/{k}.wav']))
    tail=1.3 if k==max(S) else 0.5
    out=[];j=0;ws=W[k]
    for tk in S[k].split():
        if j<len(ws) and (norm(ws[j][0])==norm(tk) or norm(tk).startswith(norm(ws[j][0])) or norm(ws[j][0]).startswith(norm(tk))):
            out.append([tk,round(ws[j][1]/sp+0.15,3)]); j+=1
        else: out.append([tk,round((out[-1][1] if out else 0)+0.2,3)])
    if j!=len(ws): print('ALINHAMENTO', k, j, len(ws))
    e=round(t+0.15+d+tail,3); TL.append(dict(id=k,s=round(t,3),e=e,vstart=round(t+0.15,3),vdur=d,words=out)); t=e
json.dump(TL,open(f'{D}/timeline.json','w'),ensure_ascii=False)
for o in TL: print(o['id'],round(o['e']-o['s'],1))
print('TOTAL',round(t,2))
