import asyncio, json, edge_tts, sys
async def main():
    text=open('job/roteiro.txt',encoding='utf-8').read().replace('\n',' ')
    for voice,name in [('pt-BR-ThalitaMultilingualNeural','thalita'),('pt-BR-AntonioNeural','antonio')]:
        c=edge_tts.Communicate(text,voice,rate='+8%',boundary='WordBoundary')
        words=[];audio=bytearray()
        async for ch in c.stream():
            if ch['type']=='audio': audio+=ch['data']
            elif ch['type']=='WordBoundary':
                words.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7})
        open(f'out/voz_{name}.mp3','wb').write(audio)
        json.dump(words,open(f'out/words_{name}.json','w'),ensure_ascii=False)
        print(name,len(words),words[-1])
asyncio.run(main())
