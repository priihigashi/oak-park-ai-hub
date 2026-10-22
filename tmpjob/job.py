import requests,os,json,subprocess
os.makedirs('out/athena',exist_ok=True); log=[]
r=requests.get("https://storage.googleapis.com/xi-backend/database/workspace/cfd0c30d08bb461c800962f2f06538b3/content_generation/Z0wvaRegsRY0hRaj9sod/pI8aZHgyl1bSrucDETsY/content.mp3?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=xi-backend-prod%40xi-labs.iam.gserviceaccount.com%2F20261022%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20261022T225435Z&X-Goog-Expires=7200&X-Goog-SignedHeaders=host&X-Goog-Signature=2a53696075bb6c96dd3ccd74479b4eeb3f55fa0d5b340388e553d9a11875c84a95f67a8689a26b4163e1970ecf2070aab7813912e28386c4dcefac7f005326bd6d52858fe97b966e433b1514b97a94c0e34cd42ff717a6148ce724e905785ff6dcaac7d73a76d3278f7b160e702f7cf4511865be6a941de55533eed8f782e56165e2a591fde9a3091f12062c49761d4ffda71522d6fac9b4046d918df79752e1bd23f0dd3de752b3ffd048a8332a934d028b8e17c512720cb55684563f3b52d67fd1c728567f7f12265ccba3f312a4c91cdbfc39bc14f4a556e425fcff6af684951d85457df122f8d31f9c16f58226d6c6e5217fa1f844d15a1e16570114a26b",timeout=120); open('out/athena/s2_new.mp3','wb').write(r.content); log.append(f'dl {r.status_code} {len(r.content)}')
subprocess.run('pip install -q faster-whisper',shell=True)
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
segs,info=m.transcribe('out/athena/s2_new.mp3',language='pt',word_timestamps=True,vad_filter=False)
W=[]
for s in segs:
    for w in s.words: W.append({'w':w.word.strip(),'s':round(w.start,3),'e':round(w.end,3)})
json.dump(W,open('out/athena/s2_new_words.json','w'),ensure_ascii=False)
log.append(f'words {len(W)} '+' '.join(w['w'] for w in W))
open('out/log.txt','w').write('\n'.join(log)); print(log)
