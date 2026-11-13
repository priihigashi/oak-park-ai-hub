import asyncio, json, edge_tts, sys
V=sys.argv[1] if len(sys.argv)>1 else "pt-BR-ThalitaMultilingualNeural"
N=json.load(open('narr.json'))
async def one(seg):
    c=edge_tts.Communicate(seg['t'],V,boundary="WordBoundary")
    audio=b'';words=[]
    async for ch in c.stream():
        if ch['type']=='audio': audio+=ch['data']
        elif ch['type']=='WordBoundary': words.append({'t':ch['offset']/1e7,'d':ch['duration']/1e7,'w':ch['text']})
    open(f"out/{seg['id']}.mp3",'wb').write(audio)
    return words
async def main():
    res={}
    for s in N: res[s['id']]=await one(s)
    json.dump(res,open('out/words.json','w'),ensure_ascii=False)
asyncio.run(main())
