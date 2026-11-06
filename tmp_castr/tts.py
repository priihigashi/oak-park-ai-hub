import asyncio, json, edge_tts, os, sys
V=sys.argv[1] if len(sys.argv)>1 else "pt-BR-ThalitaMultilingualNeural"
os.makedirs("tts",exist_ok=True)
async def one(l):
    c=edge_tts.Communicate(l["text"],V,boundary="WordBoundary")
    words=[];f=open(f"tts/{l['id']}.mp3","wb")
    async for ch in c.stream():
        if ch["type"]=="audio": f.write(ch["data"])
        elif ch["type"]=="WordBoundary":
            words.append({"w":ch["text"],"s":ch["offset"]/1e7,"e":(ch["offset"]+ch["duration"])/1e7})
    f.close(); json.dump(words,open(f"tts/{l['id']}.json","w"),ensure_ascii=False)
async def main():
    for l in json.load(open("lines.json")): await one(l)
asyncio.run(main())
