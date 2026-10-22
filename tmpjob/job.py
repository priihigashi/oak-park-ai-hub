import subprocess, sys, os, re, json, glob
os.makedirs('out/clip', exist_ok=True)
log=[]
def sh(c):
    r=subprocess.run(c,shell=True,capture_output=True,text=True); log.append('$ '+c[:150]+'\n'+(r.stdout[-800:]+r.stderr[-1500:])); return r
sh('pip install -q -U yt-dlp')
CK=''
if os.environ.get('PRI_OP_YT_COOKIES','').strip():
    open('/tmp/ck.txt','w').write(os.environ['PRI_OP_YT_COOKIES']); CK='--cookies /tmp/ck.txt'
log.append('cookies '+str(bool(CK)))
def t2s(t):
    h,m,s=t.replace(',','.').split(':'); return int(h)*3600+int(m)*60+float(s)
found=None
for vid in ['j4cghMn_i_k','N6f6L80pXns']:
    for client in ['default','web_safari','mweb']:
        ea='' if client=='default' else f'--extractor-args "youtube:player_client={client}"'
        r=sh(f'yt-dlp {CK} {ea} --skip-download --write-auto-subs --write-subs --sub-langs "pt.*" --convert-subs srt -o "out/clip/{vid}.%(ext)s" https://www.youtube.com/watch?v={vid}')
        subs=glob.glob(f'out/clip/{vid}*.srt')
        if subs: break
    if not subs: continue
    txt=open(subs[0]).read()
    blocks=re.split(r'\n\n+',txt)
    hits=[]
    for b in blocks:
        m=re.search(r'(\d\d:\d\d:\d\d[,.]\d+) --> (\d\d:\d\d:\d\d[,.]\d+)',b)
        if m and re.search(r'vingan',b,re.I): hits.append(t2s(m.group(1)))
    log.append(f'{vid} hits {hits}')
    if hits:
        found=(vid,hits[0],ea); break
if found:
    vid,t,ea=found; a=max(0,t-25); b=t+25
    sh(f'yt-dlp {CK} {ea} -f "bv*[height<=720]+ba/b[height<=720]/b" --download-sections "*{a}-{b}" --force-keyframes-at-cuts --merge-output-format mp4 -o "out/clip/mae_raw.%(ext)s" https://www.youtube.com/watch?v={vid}')
    json.dump({'vid':vid,'t':t,'a':a},open('out/clip/info.json','w'))

import asyncio
TT=json.loads(r'''{"s5": "A Justiça mandou o cabo a júri popular. Em 2024, mesmo sendo senador, Flávio Bolsonaro entrou na defesa e assinou um recurso pra tirar o caso do júri. Em 2025, defendeu outros PMs, acusados de matar quatro pessoas no Vidigal.", "s8": "Procurado pela imprensa sobre o caso, ele não respondeu. E você, o que acha da proposta defendida pelo Flávio de acabar com a marcação nas balas da polícia?"}''')
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
open('out/log.txt','w').write('\n'.join(log)[-20000:]); print('\n'.join(log)[-6000:])
