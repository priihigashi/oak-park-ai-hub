import asyncio, json, os, edge_tts
job=json.load(open('job.json')); os.makedirs('out/tts',exist_ok=True)
async def one(k,t):
    try: c=edge_tts.Communicate(t,job['voice'],rate=job['rate'],boundary="WordBoundary")
    except TypeError: c=edge_tts.Communicate(t,job['voice'],rate=job['rate'])
    words=[]
    with open(f'out/tts/{k}.mp3','wb') as f:
        async for ch in c.stream():
            if ch['type']=='audio': f.write(ch['data'])
            elif ch['type']=='WordBoundary': words.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7})
    json.dump(words,open(f'out/tts/{k}.json','w'),ensure_ascii=False)
async def main():
    for k,t in job['lines'].items(): await one(k,t)
asyncio.run(main())
