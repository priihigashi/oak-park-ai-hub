import asyncio, json, os, edge_tts
job=json.load(open('tmp_rj/job.json'))
os.makedirs('tmp_rj/out',exist_ok=True)
async def one(s):
    kw=dict(voice=job['voice'], rate=job['rate'])
    try: c=edge_tts.Communicate(s['text'], boundary='WordBoundary', **kw)
    except TypeError: c=edge_tts.Communicate(s['text'], **kw)
    words=[]; f=open(f"tmp_rj/out/{s['id']}.mp3",'wb')
    async for ch in c.stream():
        if ch['type']=='audio': f.write(ch['data'])
        elif ch['type']=='WordBoundary': words.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7})
    f.close(); json.dump(words,open(f"tmp_rj/out/{s['id']}.json",'w'),ensure_ascii=False)
async def main():
    for s in job['scenes']: await one(s)
asyncio.run(main())
