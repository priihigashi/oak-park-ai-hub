"""Voz provisória grátis (edge-tts, Thalita) por cena + tempos por palavra.
Uso: python3 tts_edge.py <pasta_do_reel>   (lê script.json; grava tts/<cena>.mp3 e words.json)
words.json = {cena: [[palavra, início_s, duração_s], ...]} — mesmo formato que build.py espera."""
import asyncio, json, os, sys
import edge_tts

VOICE = os.environ.get('VOICE', 'pt-BR-ThalitaMultilingualNeural')
D = sys.argv[1]
S = json.load(open(f'{D}/script.json'))
os.makedirs(f'{D}/tts', exist_ok=True)

async def one(k, text):
    words = []
    with open(f'{D}/tts/{k}.mp3', 'wb') as f:
        try:
            c = edge_tts.Communicate(text, VOICE, boundary='WordBoundary')
        except TypeError:
            c = edge_tts.Communicate(text, VOICE)
        async for ch in c.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                words.append([ch['text'], round(ch['offset'] / 1e7, 4), round(ch['duration'] / 1e7, 4)])
    return words

async def main():
    W = {}
    for k, text in S.items():
        for attempt in range(3):
            try:
                W[k] = await one(k, text); break
            except Exception as e:
                print('retry', k, e)
                await asyncio.sleep(3)
        print(k, len(W.get(k, [])), 'palavras')
    json.dump(W, open(f'{D}/words.json', 'w'), ensure_ascii=False)

asyncio.run(main())
