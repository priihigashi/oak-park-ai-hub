import json,os,asyncio,subprocess
os.makedirs('out',exist_ok=True)
job=json.load(open('job/job.json'))
for t in job.get('transcribe',[]):
    from faster_whisper import WhisperModel
    m=WhisperModel(t.get('model','medium'),device='cpu',compute_type='int8')
    segs,info=m.transcribe(t['file'],language='pt',word_timestamps=True,beam_size=5,vad_filter=False)
    out=[{"s":s.start,"e":s.end,"t":s.text,"w":[(w.start,w.end,w.word) for w in s.words]} for s in segs]
    json.dump(out,open('out/'+t['out'],'w'),ensure_ascii=False,indent=0)
async def tts(item):
    import edge_tts
    c=edge_tts.Communicate(item['text'],item.get('voice','pt-BR-ThalitaMultilingualNeural'),rate=item.get('rate','+0%'),boundary='WordBoundary')
    words=[];audio=b''
    async for ch in c.stream():
        if ch['type']=='audio': audio+=ch['data']
        elif ch['type']=='WordBoundary': words.append([ch['offset']/1e7,(ch['offset']+ch['duration'])/1e7,ch['text']])
    open('out/'+item['id']+'.mp3','wb').write(audio)
    json.dump(words,open('out/'+item['id']+'.json','w'),ensure_ascii=False)
async def main():
    for it in job.get('tts',[]):
        for k in range(3):
            try:
                await tts(it); break
            except Exception as e:
                print('retry',it['id'],e); await asyncio.sleep(3)
asyncio.run(main())
