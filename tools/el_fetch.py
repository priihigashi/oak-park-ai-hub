import json, os, requests, subprocess
job=json.load(open('job.json')); u=(job.get('elf') or {}).get('urls')
if not u: raise SystemExit(0)
B='https://elevenlabsusercontent.com/database/workspace/cfd0c30d08bb461c800962f2f06538b3/content_generation/'
os.makedirs('out/tts_el',exist_ok=True); log={}
for k,p in u.items():
    r=requests.get(B+p,timeout=120); log[k]=r.status_code
    if r.ok: open(f'out/tts_el/{k}.mp3','wb').write(r.content)
json.dump(log,open('out/tts_el/fetch.json','w'))
subprocess.run('pip install -q faster-whisper',shell=True)
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
L=job['elf'].get('lines',{})
for k in u:
    f=f'out/tts_el/{k}.mp3'
    if not os.path.exists(f): continue
    segs,_=m.transcribe(f,language='pt',word_timestamps=True,initial_prompt=L.get(k,'')[:400])
    W=[{'w':w.word.strip(),'s':round(w.start,3),'e':round(w.end,3)} for s in segs for w in s.words]
    json.dump(W,open(f'out/tts_el/{k}.words.json','w'),ensure_ascii=False)
