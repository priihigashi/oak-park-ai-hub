import os, json, subprocess, sys, traceback
os.makedirs('out', exist_ok=True)
log=open('out/log.txt','w')
def L(*a): print(*a); print(*a,file=log); log.flush()
import requests
urls=json.load(open('tmpjob/el_urls.json'))
for k,u in urls.items():
    try:
        r=requests.get(u,timeout=120); open(f'out/{k}.mp3','wb').write(r.content); L('dl',k,r.status_code,len(r.content))
    except Exception: L('dl fail',k,traceback.format_exc())
os.environ['HF_HUB_DISABLE_XET']='1'
subprocess.run([sys.executable,'-m','pip','install','-q','faster-whisper'],check=False)
from faster_whisper import WhisperModel
m=WhisperModel('medium',compute_type='int8')
for k in urls:
    try:
        segs,_=m.transcribe(f'out/{k}.mp3',language='pt',word_timestamps=True)
        words=[{'t':w.start,'d':w.end-w.start,'w':w.word.strip()} for s in segs for w in s.words]
        json.dump(words,open(f'out/{k}.json','w'),ensure_ascii=False)
        L('asr',k,len(words),' '.join(x['w'] for x in words)[:300])
    except Exception: L('asr fail',k,traceback.format_exc())
