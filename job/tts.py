import asyncio,json,edge_tts,os
L=json.load(open('job/lines.json'));os.makedirs('job_out',exist_ok=True)
async def one(k,t):
    c=edge_tts.Communicate(t,'pt-BR-ThalitaMultilingualNeural',rate='+8%',boundary='WordBoundary')
    words=[];f=open(f'job_out/{k}.mp3','wb')
    async for ch in c.stream():
        if ch['type']=='audio': f.write(ch['data'])
        elif ch['type']=='WordBoundary': words.append([ch['offset']/1e7,(ch['offset']+ch['duration'])/1e7,ch['text']])
    f.close();json.dump(words,open(f'job_out/{k}.json','w'),ensure_ascii=False)
async def main():
    for k,t in L.items(): await one(k,t)
asyncio.run(main())
