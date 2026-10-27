import json,asyncio,edge_tts,os,time
j=json.load(open('job.json'));os.makedirs('out',exist_ok=True)
async def go(k,t,voice):
    try: c=edge_tts.Communicate(t,voice,rate=j['rate'],boundary='WordBoundary')
    except TypeError: c=edge_tts.Communicate(t,voice,rate=j['rate'])
    words=[];buf=b''
    async for ch in c.stream():
        if ch['type']=='audio': buf+=ch['data']
        elif ch['type'] in ('WordBoundary','SentenceBoundary'): words.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7,'t':ch['type']})
    open(f'out/{k}.mp3','wb').write(buf); json.dump({'voice':voice,'words':words},open(f'out/{k}.json','w'))
for k,t in j['items'].items():
    for voice in [j['voice'],'en-US-AndrewNeural','en-US-GuyNeural']:
        ok=False
        for a in range(3):
            try: asyncio.run(go(k,t,voice)); ok=True; print('ok',k,voice); break
            except Exception as ex: print('fail',k,voice,a,ex); time.sleep(5)
        if ok: break
