import json, subprocess
from faster_whisper import WhisperModel
subprocess.run(['ffmpeg','-y','-loglevel','error','-i','out/orig.mp4','-ar','16000','-ac','1','/tmp/full.wav'],check=True)
m=WhisperModel('medium',compute_type='int8')
segs,_=m.transcribe('/tmp/full.wav',language='pt',word_timestamps=True,vad_filter=True)
out=[]
for s in segs:
    out.append({'s':round(s.start,2),'e':round(s.end,2),'t':s.text.strip()})
json.dump(out,open('res/full.json','w'),ensure_ascii=False,indent=0)
open('res/full.txt','w').write('\n'.join(f"[{x['s']:.1f}] {x['t']}" for x in out))
