"""Monta seg/*.wav + timeline.json a partir de tts/<cena>.mp3 + words.json (tempos crus da voz) + speeds.json.
Também encurta as pausas DENTRO da fala: todo silêncio > 0,18 s vira 0,10 s (pontas cortadas para 0,05 s).
Uso: python3 build.py   (rodar de novo sempre que trocar a voz; velocidades por cena vêm de speeds.json)"""
import json,subprocess,re,os,numpy as np,wave
D=os.path.dirname(os.path.abspath(__file__)); SR=48000
W=json.load(open(f'{D}/words.json')); S=json.load(open(f'{D}/script.json')); SP=json.load(open(f'{D}/speeds.json'))['speeds']
KEEP,MINSIL,EDGE,THR=0.10,0.18,0.05,0.012
norm=lambda w: re.sub(r'[^\wÀ-ú]','',w.lower())
def _remap_time(t,cmap):
    prev=(0,0)
    for i in range(0,len(cmap),2):
        a,na=cmap[i]; b,nb=cmap[i+1]
        if t<a: return prev[1]+(t-prev[0])
        if t<b: return nb
        prev=(b,nb)
    return prev[1]+(t-prev[0])
def squeeze(k):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',f'{D}/tts/{k}.mp3','-f','s16le','-ac','1','-ar',str(SR),'-'])
    x=np.frombuffer(raw,np.int16).astype(np.float32)/32768
    fr=int(.01*SR); n=len(x)//fr
    rms=np.sqrt((x[:n*fr].reshape(n,fr)**2).mean(1)); quiet=rms<THR
    segs=[]; i=0  # (start,end) seconds of silences
    while i<n:
        if quiet[i]:
            j=i
            while j<n and quiet[j]: j+=1
            segs.append((i*fr/SR,j*fr/SR)); i=j
        else: i+=1
    dur=len(x)/SR; cuts=[]  # (start,end,keep)
    for a,b in segs:
        if a==0: cuts.append((0,b,EDGE))
        elif b>=dur-0.011: cuts.append((a,dur,EDGE))
        elif b-a>MINSIL: cuts.append((a,b,KEEP))
    out=[];pos=0;cmap=[]  # cmap: (old_start, new_start) breakpoints
    newt=0
    for a,b,keep in cuts:
        out.append(x[int(pos*SR):int(a*SR)]); newt+=a-pos; cmap.append((a,newt))
        k2=min(keep,b-a); out.append(x[int(a*SR):int((a+k2)*SR)]); newt+=k2; pos=b; cmap.append((b,newt))
    out.append(x[int(pos*SR):]); y=np.concatenate(out)
    remap=lambda t: _remap_time(t,cmap)
    p=f'{D}/seg/{k}_sq.wav'
    with wave.open(p,'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y,-1,1)*32767).astype(np.int16).tobytes())
    return p,remap,dur-len(y)/SR
TL=[];t=0;saved=0
ORDER=json.load(open(f'{D}/speeds.json')).get('order') or sorted(S)
for k in ORDER:
    sp=SP[k]; p,remap,cut=squeeze(k); saved+=cut/sp
    subprocess.run(['ffmpeg','-v','error','-y','-i',p,'-filter:a',f'atempo={sp}','-ar',str(SR),f'{D}/seg/{k}.wav'],check=True); os.remove(p)
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{D}/seg/{k}.wav']))
    tail=1.3 if k==ORDER[-1] else 0.4
    out=[];j=0;ws=W[k]
    for tk in S[k].split():
        if j<len(ws) and (norm(ws[j][0])==norm(tk) or norm(tk).startswith(norm(ws[j][0])) or norm(ws[j][0]).startswith(norm(tk))):
            out.append([tk,round(remap(ws[j][1])/sp+0.12,3)]); j+=1
        else: out.append([tk,round((out[-1][1] if out else 0)+0.2,3)])
    if j!=len(ws): print('ALINHAMENTO', k, j, len(ws))
    e=round(t+0.12+d+tail,3); TL.append(dict(id=k,s=round(t,3),e=e,vstart=round(t+0.12,3),vdur=d,words=out)); t=e
json.dump(TL,open(f'{D}/timeline.json','w'),ensure_ascii=False)
for o in TL: print(o['id'],round(o['e']-o['s'],1))
print('TOTAL',round(t,2),'· silêncio cortado',round(saved,1),'s')
