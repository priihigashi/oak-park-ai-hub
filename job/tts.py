import json,asyncio,edge_tts,os
j=json.load(open('job.json'));os.makedirs('out',exist_ok=True)
async def go(k,t):
    c=edge_tts.Communicate(t,j['voice'],rate=j['rate'],boundary='WordBoundary')
    words=[];f=open(f'out/{k}.mp3','wb')
    async for ch in c.stream():
        if ch['type']=='audio': f.write(ch['data'])
        elif ch['type']=='WordBoundary': words.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7})
    f.close(); json.dump(words,open(f'out/{k}.json','w'))
for k,t in j['items'].items(): asyncio.run(go(k,t))
