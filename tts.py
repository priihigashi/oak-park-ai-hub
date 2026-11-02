import json,asyncio,edge_tts,os
J=json.load(open('job.json'));os.makedirs('out',exist_ok=True)
async def one(k,t):
    c=edge_tts.Communicate(t,J['voice'],rate=J['rate'],boundary='WordBoundary')
    words=[]
    with open(f'out/{k}.mp3','wb') as f:
        async for ch in c.stream():
            if ch['type']=='audio': f.write(ch['data'])
            elif ch['type']=='WordBoundary': words.append([ch['text'],ch['offset']/1e7,(ch['offset']+ch['duration'])/1e7])
    json.dump(words,open(f'out/{k}.json','w'),ensure_ascii=False)
async def main():
    for k,t in J['scenes']: await one(k,t)
asyncio.run(main())
