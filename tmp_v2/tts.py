import asyncio,json,edge_tts
L=json.load(open('tmp_v2/lines.json'))
async def one(i,t):
    c=edge_tts.Communicate(t,"pt-BR-ThalitaMultilingualNeural",rate="+8%",boundary="WordBoundary")
    wb=[];f=open(f'tmp_v2/tts/n{i}.mp3','wb')
    async for ch in c.stream():
        if ch['type']=='audio': f.write(ch['data'])
        elif ch['type']=='WordBoundary': wb.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7})
    f.close(); json.dump(wb,open(f'tmp_v2/tts/n{i}.json','w'),ensure_ascii=False)
async def main():
    for i,t in enumerate(L): await one(i,t)
asyncio.run(main())
