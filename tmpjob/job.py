import requests,os,json,subprocess
os.makedirs('out/athena',exist_ok=True); log=[]
r=requests.get("https://storage.googleapis.com/xi-backend/database/workspace/cfd0c30d08bb461c800962f2f06538b3/content_generation/RYk0vMVuFhuoNcKv5VVz/enP0acK8LOxw2QZtAYVJ/content.mp3?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=xi-backend-prod%40xi-labs.iam.gserviceaccount.com%2F20261022%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20261022T225921Z&X-Goog-Expires=7200&X-Goog-SignedHeaders=host&X-Goog-Signature=9dba583721afe3aaab350503bf384fe3a00ad4000205158e1f0d26c977d9f66ba5853d73c0b60a1b1c867ba7a9c047da45ed06fb7f73407dbfd05f50c92dc793ea53e08ee8d5974462f5738161053299dad706940f5bc9ff1b4b29352b988de0610395d88483c2887fe867a17ac888164b1df589908fd252782a7941a36dd2541b3deaa23592bb23fdbd4037248d1087bf6728637484e9711127b3ea570d00c119e56327a8dbfc749888cdad9e7f7173f0f019fa49260c10be5e124aa7f5d1a78c5c36894d4082d5ad52c3b33f0f67203634e4c8ccc70c55cfc16667fe94795c632370b4d28bd24db7420de43ed2a4a1e54fbb2dbf36756e3765625c6d1ffdb1",timeout=120); open('out/athena/s3_new.mp3','wb').write(r.content); log.append(f'dl {r.status_code} {len(r.content)}')
subprocess.run('pip install -q faster-whisper',shell=True)
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
segs,info=m.transcribe('out/athena/s3_new.mp3',language='pt',word_timestamps=True,vad_filter=False)
W=[]
for s in segs:
    for w in s.words: W.append({'w':w.word.strip(),'s':round(w.start,3),'e':round(w.end,3)})
json.dump(W,open('out/athena/s3_new_words.json','w'),ensure_ascii=False)
log.append(f'words {len(W)} '+' '.join(w['w'] for w in W))
open('out/log.txt','w').write('\n'.join(log)); print(log)
