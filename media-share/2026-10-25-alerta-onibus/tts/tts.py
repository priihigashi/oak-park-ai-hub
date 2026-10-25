import asyncio,json,sys,os
import edge_tts
J=json.load(open(sys.argv[1])); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
async def one(s):
    c=edge_tts.Communicate(s['text'],J['voice'],rate=J['rate'],boundary='WordBoundary')
    words=[]
    with open(f"{out}/{s['id']}.mp3",'wb') as f:
        async for ch in c.stream():
            if ch['type']=='audio': f.write(ch['data'])
            elif ch['type']=='WordBoundary': words.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7})
    json.dump(words,open(f"{out}/{s['id']}.json",'w'),ensure_ascii=False)
async def main():
    for s in J['scenes']: await one(s)
asyncio.run(main())
