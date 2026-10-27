import asyncio, json, os, edge_tts
job=json.load(open('tmp_rj/job.json'))
os.makedirs('tmp_rj/out',exist_ok=True)
async def one(s, voice, rate):
    try: c=edge_tts.Communicate(s['text'], voice=voice, rate=rate, boundary='WordBoundary')
    except TypeError: c=edge_tts.Communicate(s['text'], voice=voice, rate=rate)
    words=[]; buf=bytearray()
    async for ch in c.stream():
        if ch['type']=='audio': buf+=ch['data']
        elif ch['type']=='WordBoundary': words.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7})
    if not buf: raise RuntimeError('no audio')
    open(f"tmp_rj/out/{s['id']}.mp3",'wb').write(buf)
    json.dump({'voice':voice,'words':words},open(f"tmp_rj/out/{s['id']}.json",'w'),ensure_ascii=False)
async def main():
    for s in job['scenes']:
        done=False
        for voice,rate in [(job['voice'],job['rate'])]*8:
            try: await one(s,voice,rate); done=True; print(s['id'],voice); break
            except Exception as e: print('retry',s['id'],voice,e); await asyncio.sleep(8)
        if not done: raise SystemExit('fail '+s['id'])
asyncio.run(main())
