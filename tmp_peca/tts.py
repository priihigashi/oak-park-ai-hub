import asyncio, json, os, edge_tts
VOICE = os.environ.get("VOICE", "pt-BR-ThalitaMultilingualNeural")
d = json.load(open("tmp_peca/narr.json"))
os.makedirs("tts_out", exist_ok=True)
async def one(k, text):
    try:
        c = edge_tts.Communicate(text, VOICE, rate="+6%", boundary="WordBoundary")
    except TypeError:
        c = edge_tts.Communicate(text, VOICE, rate="+6%")
    words = []
    with open(f"tts_out/{k}.mp3", "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] in ("WordBoundary", "SentenceBoundary"):
                words.append({"t": ch["offset"]/1e7, "d": ch["duration"]/1e7, "w": ch["text"], "k": ch["type"]})
    json.dump(words, open(f"tts_out/{k}.json", "w"), ensure_ascii=False)
async def main():
    for k, v in d.items():
        await one(k, v)
asyncio.run(main())
