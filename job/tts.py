import asyncio, json, os, edge_tts
OUT = "out/tts"; os.makedirs(OUT, exist_ok=True)
job = json.load(open("job/tts.json"))
VOICE = job.get("voice", "pt-BR-ThalitaMultilingualNeural")
RATE = job.get("rate", "+12%")

async def one(i, text):
    c = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
    words = []
    with open(f"{OUT}/s{i:02d}.mp3", "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"w": ch["text"], "t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7})
    json.dump(words, open(f"{OUT}/s{i:02d}.json", "w"), ensure_ascii=False)

async def main():
    for i, t in enumerate(job["scenes"]):
        await one(i, t)
asyncio.run(main())
print("ok", len(job["scenes"]))
