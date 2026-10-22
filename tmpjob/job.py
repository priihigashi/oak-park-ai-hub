import requests,os,json,subprocess
os.makedirs('out/athena',exist_ok=True); log=[]
r=requests.get("https://storage.googleapis.com/xi-backend/database/workspace/cfd0c30d08bb461c800962f2f06538b3/content_generation/LgspkjOjyxQVZQob1Pjs/qU5EuSOrxF0GedgS6fkr/content.mp3?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=xi-backend-prod%40xi-labs.iam.gserviceaccount.com%2F20261022%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20261022T224904Z&X-Goog-Expires=7200&X-Goog-SignedHeaders=host&X-Goog-Signature=41a250e85f66f4fdccd8679276e159cee028b3de1be0e6f621645aadd85e0d95a3a769cabe7bb0e8bd4ac9353cfb0f86a13aa4095e5bb966c7c3afaf65db21dab49f1b8065fa0e0581b0f64c9eeeb8717e9b0dc70a54d757a2e30388258c27637e6447700cb36183445c7ae5a6587bf972c774de06793d5921fdeac18f5b922ed2df98107e2ec60265acfb31194fefd9136051c2f32211fef86c3a9c8ecc4d5565ec8cdbd24c8d14786d7163b435881533e0aaafbf3d0121850633a8c92fa8b173cffa06713829f23eed3f420e0729bf751b73fdfbfdebcf1ac19517d36e7784042c36ca29ffed4bd2c4cd3b3914080523da87a5bd38f4c8ab89560b1b550a89",timeout=120); open('out/athena/full.mp3','wb').write(r.content); log.append(f'dl {r.status_code} {len(r.content)}')
subprocess.run('pip install -q faster-whisper',shell=True)
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
segs,info=m.transcribe('out/athena/full.mp3',language='pt',word_timestamps=True,vad_filter=False)
W=[]
for s in segs:
    for w in s.words: W.append({'w':w.word.strip(),'s':round(w.start,3),'e':round(w.end,3)})
json.dump(W,open('out/athena/words.json','w'),ensure_ascii=False)
log.append(f'words {len(W)}')
open('out/log.txt','w').write('\n'.join(log)); print(log)
