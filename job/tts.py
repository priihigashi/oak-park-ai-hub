import asyncio, json, edge_tts, sys
async def main():
    t=open('job/narr.txt').read().replace('\n',' ')
    c=edge_tts.Communicate(t,'pt-BR-ThalitaMultilingualNeural',rate='+8%',boundary='WordBoundary')
    words=[];f=open('out/voz.mp3','wb')
    async for ch in c.stream():
        if ch['type']=='audio': f.write(ch['data'])
        elif ch['type']=='WordBoundary': words.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7})
    json.dump(words,open('out/words.json','w'),ensure_ascii=False)
asyncio.run(main())
