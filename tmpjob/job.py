import os, json, subprocess, requests
os.makedirs('out/clip',exist_ok=True); log=[]
AK=os.environ.get('APIFY_API_KEY','')
subprocess.run('pip install -q imageio-ffmpeg',shell=True)
import imageio_ffmpeg; FF=imageio_ffmpeg.get_ffmpeg_exe()
def urls(o):
    if isinstance(o,dict):
        for k,v in o.items(): yield from ((k,x) for x in ([v] if isinstance(v,str) else [])) ; 
        for v in o.values():
            if isinstance(v,(dict,list)): yield from urls(v)
    elif isinstance(o,list):
        for v in o: yield from urls(v)
ok=False
for rid in ['cm5KTGBGEeFOeR5pG','H5z1Pzx8Fm4KYMLEj']:
    if ok: break
    r=requests.get(f'https://api.apify.com/v2/actor-runs/{rid}?token={AK}',timeout=60).json()['data']
    items=requests.get(f'https://api.apify.com/v2/datasets/{r["defaultDatasetId"]}/items?token={AK}',timeout=60).json()
    for k,v in urls(items):
        if not v.startswith('http') or 'manifest.googlevideo' in v or 'ytimg' in v or 'youtube.com/watch' in v: continue
        try:
            with requests.get(v if 'api.apify.com' not in v or 'token=' in v else v+('&' if '?' in v else '?')+'token='+AK,stream=True,timeout=600) as rr:
                with open('/tmp/a.mp4','wb') as f:
                    for ch in rr.iter_content(1<<20): f.write(ch)
            sz=os.path.getsize('/tmp/a.mp4'); log.append(f'{rid} {k} {sz}')
            if sz>1000000:
                p=subprocess.run([FF,'-y','-ss','0','-i','/tmp/a.mp4','-t','75','-c:v','libx264','-preset','veryfast','-crf','22','-vf','scale=-2:720','-c:a','aac','-b:a','160k','out/clip/mae_raw.mp4'],capture_output=True,text=True)
                log.append('ff rc '+str(p.returncode)+' '+p.stderr[-300:])
                if p.returncode==0: ok=True; break
        except Exception as e: log.append(f'err {k} {e!r}')
import asyncio
TT=json.loads(r'''{"s6": "O STJ negou, o Supremo também. Mas o julgamento foi adiado duas vezes: agora, só em maio de 2027.", "s8": "Procurado pela imprensa, ele não respondeu. E você, o que acha da proposta do Flávio de acabar com a marcação nas balas da polícia?"}''')
os.makedirs('out/tts',exist_ok=True)
async def one(k,t):
    import edge_tts
    c=edge_tts.Communicate(t,'pt-BR-ThalitaMultilingualNeural',rate='+18%',boundary='WordBoundary')
    w=[];a=b''
    async for ch in c.stream():
        if ch['type']=='audio': a+=ch['data']
        elif ch['type']=='WordBoundary': w.append({'w':ch['text'],'s':ch['offset']/1e7,'d':ch['duration']/1e7})
    open(f'out/tts/{k}.mp3','wb').write(a); json.dump(w,open(f'out/tts/{k}.json','w'),ensure_ascii=False); log.append(f'tts {k} {len(a)} {len(w)}w')
async def allt():
    for k,t in TT.items(): await one(k,t)
try: asyncio.run(allt())
except Exception as e: log.append('TTS FAIL '+repr(e))
open('out/log.txt','w').write('\n'.join(log)); print('\n'.join(log))
