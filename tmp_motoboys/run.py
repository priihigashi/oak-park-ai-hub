import json, os, asyncio, base64, requests, subprocess
job=json.load(open('job.json'))
os.makedirs('out',exist_ok=True)
log=open('out/log.txt','a')
UA={'User-Agent':'reel-bot/1.0 (github.com/priihigashi)'}
# faces: wikimedia search
for f in job.get('faces',[]):
    try:
        r=requests.get('https://commons.wikimedia.org/w/api.php',params={'action':'query','format':'json','generator':'search','gsrsearch':f['q']+' filetype:bitmap','gsrnamespace':6,'gsrlimit':f.get('n',5),'prop':'imageinfo','iiprop':'url|size','iiurlwidth':1400},headers=UA,timeout=30).json()
        pages=sorted(r.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',0))
        os.makedirs('out/faces',exist_ok=True)
        for k,p in enumerate(pages):
            ii=p['imageinfo'][0]; u=ii.get('thumburl') or ii['url']
            b=requests.get(u,headers=UA,timeout=60).content
            open(f"out/faces/{f['name']}_{k}.jpg",'wb').write(b)
            log.write(f"{f['name']}_{k}\t{p['title']}\t{u}\n")
    except Exception as e: log.write(f"face {f['name']} ERR {e}\n")
for u in job.get('urls',[]):
    try:
        b=requests.get(u['url'],headers=UA,timeout=60).content
        os.makedirs('out/dl',exist_ok=True); open('out/dl/'+u['name'],'wb').write(b)
    except Exception as e: log.write(f"url {u['name']} ERR {e}\n")
# whisper
w=job.get('whisper')
if w:
    from faster_whisper import WhisperModel
    m=WhisperModel(w.get('model','medium'),device='cpu',compute_type='int8')
    segs,_=m.transcribe(w['file'],language='pt',word_timestamps=True)
    words=[[round(x.start,2),round(x.end,2),x.word.strip()] for s in segs for x in s.words]
    json.dump(words,open('out/'+w['out'],'w'),ensure_ascii=False)
# tts
import edge_tts
async def tts(s):
    c=edge_tts.Communicate(s['text'],s.get('voice','pt-BR-ThalitaMultilingualNeural'),rate=s.get('rate','+0%'),boundary='WordBoundary')
    os.makedirs('out/tts',exist_ok=True)
    au=b''; wb=[]
    async for ch in c.stream():
        if ch['type']=='audio': au+=ch['data']
        elif ch['type']=='WordBoundary': wb.append([ch['offset']/1e7,(ch['offset']+ch['duration'])/1e7,ch['text']])
    open(f"out/tts/{s['id']}.mp3",'wb').write(au); json.dump(wb,open(f"out/tts/{s['id']}.json",'w'),ensure_ascii=False)
async def main():
    for s in job.get('tts',[]):
        try: await tts(s)
        except Exception as e: log.write(f"tts {s['id']} ERR {e}\n")
asyncio.run(main())
log.close()
