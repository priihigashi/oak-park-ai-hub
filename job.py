import asyncio,json,edge_tts,os
J=json.load(open('job_texts.json'))
os.makedirs('out',exist_ok=True)
async def one(k,t):
    c=edge_tts.Communicate(t,'pt-BR-ThalitaMultilingualNeural',rate='+10%',boundary='WordBoundary')
    words=[];f=open(f'out/{k}.mp3','wb')
    async for ch in c.stream():
        if ch['type']=='audio':f.write(ch['data'])
        elif ch['type']=='WordBoundary':words.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7})
    f.close();json.dump(words,open(f'out/{k}.json','w'),ensure_ascii=False)
async def main():
    for k,t in J.items(): await one(k,t)
asyncio.run(main())
