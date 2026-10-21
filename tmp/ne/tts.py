import asyncio,json,os,sys,edge_tts
D=sys.argv[1]; S=json.load(open(f'{D}/script.json')); os.makedirs(f'{D}/out/tts',exist_ok=True)
V=os.environ.get('VOICE','pt-BR-AntonioNeural'); R=os.environ.get('RATE','+10%')
async def one(k,t):
    w=[]
    with open(f'{D}/out/tts/{k}.mp3','wb') as f:
        c=edge_tts.Communicate(t,V,rate=R,boundary='WordBoundary')
        async for ch in c.stream():
            if ch['type']=='audio': f.write(ch['data'])
            elif ch['type']=='WordBoundary': w.append([ch['text'],round(ch['offset']/1e7,4),round(ch['duration']/1e7,4)])
    return w
async def main():
    W={}
    for k,t in S.items():
        for a in range(3):
            try: W[k]=await one(k,t); break
            except Exception as e: print('retry',k,e); await asyncio.sleep(3)
    json.dump(W,open(f'{D}/out/tts/words.json','w'),ensure_ascii=False)
asyncio.run(main())
