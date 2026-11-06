import asyncio,json,os,edge_tts
J=json.load(open('tmp_cbs/job.json')); os.makedirs('out_cbs',exist_ok=True)
async def one(v,k,t):
    c=edge_tts.Communicate(t,v,rate=J.get("rate","+0%"),boundary="WordBoundary"); wb=[]; f=open(f'out_cbs/{k}_{v}.mp3','wb')
    async for ch in c.stream():
        if ch["type"]=="audio": f.write(ch["data"])
        elif ch["type"]=="WordBoundary": wb.append([ch["text"],ch["offset"]/1e7,(ch["offset"]+ch["duration"])/1e7])
    f.close(); json.dump(wb,open(f'out_cbs/{k}_{v}.json','w'),ensure_ascii=False)
async def main():
    for v in J["voices"]:
        for k,t in J["segs"].items():
            for i in range(3):
                try: await one(v,k,t); break
                except Exception as e: print('retry',v,k,e); await asyncio.sleep(3)
asyncio.run(main())
