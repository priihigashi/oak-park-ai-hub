import asyncio,json,edge_tts,os
J=json.load(open('job_texts.json'))
os.makedirs('out',exist_ok=True)
VOICES=[('pt-BR-ThalitaMultilingualNeural','+10%'),('pt-BR-FranciscaNeural','+12%')]
async def one(k,t,v,r):
    c=edge_tts.Communicate(t,v,rate=r,boundary='WordBoundary')
    words=[];buf=b''
    async for ch in c.stream():
        if ch['type']=='audio':buf+=ch['data']
        elif ch['type']=='WordBoundary':words.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7})
    open(f'out/{k}.mp3','wb').write(buf);json.dump(words,open(f'out/{k}.json','w'),ensure_ascii=False)
async def main():
    used={}
    for k,t in J.items():
        ok=False
        for v,r in VOICES:
            for a in range(3):
                try:
                    await one(k,t,v,r);ok=True;used[k]=v;print(k,v);break
                except Exception as e:
                    print('retry',k,v,e);await asyncio.sleep(3)
            if ok:break
    json.dump(used,open('out/voices.json','w'))
asyncio.run(main())
