import asyncio,json,edge_tts,os,subprocess
L=json.load(open('job/lines.json'));os.makedirs('job_out',exist_ok=True)
log=open('job_out/tts_log.txt','w')
async def one(k,t):
    for voice,rate in [('pt-BR-ThalitaMultilingualNeural','+8%'),('pt-BR-ThalitaMultilingualNeural','+0%'),('pt-BR-ThalitaNeural','+8%'),('en-US-AndrewMultilingualNeural','+8%')]:
        try:
            c=edge_tts.Communicate(t,voice,rate=rate)
            await c.save(f'job_out/{k}.mp3'); log.write(f'{k} {voice} {rate} OK\n'); return
        except Exception as e: log.write(f'{k} {voice} {rate} FAIL {e}\n')
async def main():
    for k,t in L.items(): await one(k,t)
asyncio.run(main()); log.close()
from faster_whisper import WhisperModel
m=WhisperModel('small',compute_type='int8')
import numpy as np
for k in L:
    p=f'job_out/{k}.mp3'
    if not os.path.exists(p): continue
    raw=subprocess.run(['ffmpeg','-loglevel','error','-i',p,'-f','f32le','-ac','1','-ar','16000','-'],capture_output=True).stdout
    segs,_=m.transcribe(np.frombuffer(raw,dtype=np.float32),language='pt',word_timestamps=True,initial_prompt=L[k])
    w=[[round(x.start,2),round(x.end,2),x.word.strip()] for s in segs for x in s.words]
    json.dump(w,open(f'job_out/{k}.json','w'),ensure_ascii=False)
