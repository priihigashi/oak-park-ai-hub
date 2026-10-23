import json, asyncio, re, edge_tts
S = json.load(open('tmp/nd/script.json'))
SAY = {'PT': 'pê tê', 'PL': 'pê éle', 'PCC': 'pê cê cê', 'PFL': 'pê éfe éle'}
async def one(k, text):
    toks = text.split(); say = []
    for t in toks:
        core = re.sub(r'[^\wÀ-ú]', '', t); say.append(t.replace(core, SAY[core]) if core in SAY else t)
    c = edge_tts.Communicate(' '.join(say), 'pt-BR-ThalitaMultilingualNeural', rate='+18%', boundary='WordBoundary')
    audio = b''; wb = []
    async for ch in c.stream():
        if ch['type'] == 'audio': audio += ch['data']
        elif ch['type'] == 'WordBoundary': wb.append([ch['text'], ch['offset'] / 1e7, ch['duration'] / 1e7])
    open(f'tmp/nd/out/{k}.mp3', 'wb').write(audio)
    return k, wb
async def main():
    import os; os.makedirs('tmp/nd/out', exist_ok=True)
    R = {}
    for k, v in S.items():
        k, wb = await one(k, v); R[k] = wb
    json.dump(R, open('tmp/nd/out/wb.json', 'w'), ensure_ascii=False)
asyncio.run(main())
