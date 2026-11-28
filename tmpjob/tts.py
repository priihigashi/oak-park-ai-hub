import asyncio,json,edge_tts,subprocess,os
V='pt-BR-ThalitaMultilingualNeural'
segs=json.load(open('tmpjob/segs.json'));os.makedirs('out',exist_ok=True)
async def one(i,txt):
    c=edge_tts.Communicate(txt,V,rate='+6%',boundary='WordBoundary');ws=[];f=open(f'out/s{i}.mp3','wb')
    async for ch in c.stream():
        if ch['type']=='audio':f.write(ch['data'])
        elif ch['type']=='WordBoundary':ws.append([ch['offset']/1e7,(ch['offset']+ch['duration'])/1e7,ch['text']])
    f.close();return ws
async def main():
    res=[];t=0
    lst=open('out/list.txt','w')
    for i,(k,txt) in enumerate(segs):
        ws=await one(i,txt)
        d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'out/s{i}.mp3']))
        res.append({'k':k,'t0':round(t,3),'dur':round(d,3),'words':[[round(a+t,3),round(b+t,3),w] for a,b,w in ws]})
        lst.write(f"file 's{i}.mp3'\nfile 'gap.mp3'\n");t+=d+0.35
    lst.close();json.dump(res,open('out/timing.json','w'),ensure_ascii=False)
subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t','0.35','-q:a','4','out/gap.mp3'])
asyncio.run(main())
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i','out/list.txt','-ar','44100','-b:a','96k','out/voz.mp3'])
for f in os.listdir('out'):
    if (f.startswith('s') and f.endswith('.mp3')) or f in('gap.mp3','list.txt'):os.remove('out/'+f)
