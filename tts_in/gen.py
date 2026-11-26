import asyncio, json, os, subprocess, edge_tts
VOICES=["pt-BR-ThalitaMultilingualNeural","pt-BR-ThalitaNeural"]
async def one(seg, voice):
    c=edge_tts.Communicate(seg["text"], voice, rate="+10%", boundary="WordBoundary")
    words=[]; 
    with open(f"tts_out/{seg['id']}.mp3","wb") as f:
        async for ch in c.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary": words.append({"w":ch["text"],"t":ch["offset"]/1e7,"d":ch["duration"]/1e7})
    return words
async def main():
    os.makedirs("tts_out",exist_ok=True)
    segs=json.load(open("tts_in/narr.json")); out=[]
    for s in segs:
        for v in VOICES:
            try:
                w=await one(s,v); used=v; break
            except Exception as e: print("falhou",v,e)
        dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"tts_out/{s['id']}.mp3"]).decode())
        out.append({"id":s["id"],"voice":used,"dur":dur,"words":w})
    json.dump(out,open("tts_out/words.json","w"),ensure_ascii=False,indent=0)
asyncio.run(main())
