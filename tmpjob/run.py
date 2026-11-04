import json, re, asyncio, os, subprocess, sys, traceback
os.makedirs('out', exist_ok=True)
log = open('out/log.txt','w')
def L(*a):
    print(*a); print(*a, file=log); log.flush()
async def tts():
  import edge_tts
  d = json.load(open('tmpjob/script.json'))
  for s in d['scenes']:
    if d.get('only') and s['id'] not in d['only']: continue
    spoken = re.sub(r'\{[^|}]*\|([^}]*)\}', r'\1', s['text']).replace('¦','')
    for attempt in range(3):
      try:
        c = edge_tts.Communicate(spoken, d['voice'], rate=d['rate'], boundary="WordBoundary")
        words=[]; audio=bytearray()
        async for ch in c.stream():
            if ch['type']=='audio': audio+=ch['data']
            elif ch['type']=='WordBoundary': words.append({'t':ch['offset']/1e7,'d':ch['duration']/1e7,'w':ch['text']})
        open(f"out/{s['id']}.mp3",'wb').write(audio); json.dump(words, open(f"out/{s['id']}.json",'w'), ensure_ascii=False)
        L('tts', s['id'], len(words)); break
      except Exception: L('retry', s['id'], traceback.format_exc()[-200:])
try: asyncio.run(tts())
except Exception: L(traceback.format_exc())
