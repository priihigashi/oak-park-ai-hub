import asyncio,json,os,edge_tts
j=json.load(open('voz/job.json'));os.makedirs('voz/out',exist_ok=True)
async def one(k,t):
    c=edge_tts.Communicate(t,j['voice'],rate=j['rate'],boundary='WordBoundary')
    words=[];f=open(f'voz/out/{k}.mp3','wb')
    async for ch in c.stream():
        if ch['type']=='audio': f.write(ch['data'])
        elif ch['type']=='WordBoundary': words.append({'w':ch['text'],'a':ch['offset']/1e7,'b':(ch['offset']+ch['duration'])/1e7})
    f.close(); json.dump(words,open(f'voz/out/{k}.json','w'),ensure_ascii=False)
async def main():
    for k,t in j['scenes']: await one(k,t)
asyncio.run(main())
