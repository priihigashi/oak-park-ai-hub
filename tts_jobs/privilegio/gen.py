import asyncio, json, os, edge_tts
lines=json.load(open('tts_jobs/privilegio/lines.json'))
out='tts_out/privilegio'; os.makedirs(out,exist_ok=True)
async def main():
    vs=[v['ShortName'] for v in await edge_tts.list_voices() if v['Locale']=='pt-BR']
    json.dump(vs,open(f'{out}/voices.json','w'))
    want=[v for v in vs if any(k in v for k in ['Francisca','Thalita','Antonio'])]
    for v in want:
        meta=[]
        for i,t in enumerate(lines):
            c=edge_tts.Communicate(t,v,rate='+8%',boundary='WordBoundary')
            fn=f'{out}/{v}_{i:02d}.mp3'; words=[]
            with open(fn,'wb') as f:
                async for ch in c.stream():
                    if ch['type']=='audio': f.write(ch['data'])
                    elif ch['type']=='WordBoundary': words.append([round(ch['offset']/1e7,3),ch['text']])
            meta.append(words)
        json.dump(meta,open(f'{out}/{v}_words.json','w'),ensure_ascii=False)
asyncio.run(main())
