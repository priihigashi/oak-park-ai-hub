import os, json, asyncio, time
import edge_tts
OUT='out'; os.makedirs(OUT, exist_ok=True)
job=json.load(open('job/job.json'))
log=open(f'{OUT}/log2.txt','w')
def L(*a):
    print(*a); log.write(' '.join(map(str,a))+'\n'); log.flush()
L('edge_tts', getattr(edge_tts,'__version__','?'))
async def tts(i, text, voice, rate):
    try:
        c = edge_tts.Communicate(text, voice, rate=rate, boundary='WordBoundary')
    except TypeError:
        c = edge_tts.Communicate(text, voice, rate=rate)
    words=[]; buf=bytearray()
    async for ch in c.stream():
        if ch['type']=='audio': buf+=ch['data']
        elif ch['type']=='WordBoundary':
            words.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7})
    if not buf: raise RuntimeError('empty')
    open(f'{OUT}/{i}.mp3','wb').write(bytes(buf))
    json.dump(words, open(f'{OUT}/{i}.json','w'), ensure_ascii=False)
for n in job['narr']:
    ok=False
    for k in range(8):
        v = job['voice'] if k < 5 else 'pt-BR-FranciscaNeural'
        try:
            asyncio.run(tts(n['id'], n['text'], v, job['rate'])); L('tts ok', n['id'], k, v); ok=True; break
        except Exception as e:
            L('tts fail', n['id'], k, repr(e)); time.sleep(6+6*k)
    time.sleep(3)
log.close()
