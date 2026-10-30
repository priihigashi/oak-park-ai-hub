import asyncio, json, os, edge_tts
job=json.load(open('job.json')); os.makedirs('out/tts',exist_ok=True)
log={}
async def one(k,t,voice):
    try: c=edge_tts.Communicate(t,voice,rate=job['rate'],boundary="WordBoundary")
    except TypeError: c=edge_tts.Communicate(t,voice,rate=job['rate'])
    words=[]; buf=b''
    async for ch in c.stream():
        if ch['type']=='audio': buf+=ch['data']
        elif ch['type']=='WordBoundary': words.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7})
    open(f'out/tts/{k}.mp3','wb').write(buf)
    json.dump(words,open(f'out/tts/{k}.json','w'),ensure_ascii=False)
async def main():
    for k,t in job['lines'].items():
        if job.get('only') and k not in job['only']: continue
        for voice in [job['voice']]*6:
            try:
                await one(k,t,voice); log[k]=voice; break
            except Exception as ex:
                log[k]='err '+repr(ex)[:200]; await asyncio.sleep(10)
    json.dump(log,open('out/tts/log2.json','w'),indent=1)
asyncio.run(main())
