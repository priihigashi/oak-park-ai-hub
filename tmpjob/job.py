import os, json, re, subprocess, requests, time
os.makedirs('out/clip',exist_ok=True); log=[]
AK=os.environ.get('APIFY_API_KEY','')
vid='N6f6L80pXns'; url=f'https://www.youtube.com/watch?v={vid}'
def cut(src):
    p=subprocess.run(['ffmpeg','-y','-i',src,'-t','75','-c:v','libx264','-preset','veryfast','-crf','24','-vf','scale=-2:720','-c:a','aac','-b:a','160k','out/clip/mae_raw.mp4'],capture_output=True,text=True); log.append('ff '+p.stderr[-300:])
ok=False
def grab(items):
    for it in items:
        for k,v in it.items():
            if isinstance(v,str) and v.startswith('http') and 'youtube.com' not in v and 'i.ytimg' not in v:
                try:
                    b=requests.get(v,timeout=300).content
                    log.append(f'try {k} {len(b)}')
                    if len(b)>200000: open('/tmp/a.mp4','wb').write(b); cut('/tmp/a.mp4'); return True
                except Exception as e: log.append(f'dl err {e!r}')
    return False
for rid in ['H5z1Pzx8Fm4KYMLEj','cm5KTGBGEeFOeR5pG']:
    if ok: break
    try:
        for _ in range(30):
            r=requests.get(f'https://api.apify.com/v2/actor-runs/{rid}?token={AK}',timeout=60).json()['data']
            if r['status'] not in ('READY','RUNNING'): break
            time.sleep(10)
        log.append(f'{rid} {r["status"]}')
        items=requests.get(f'https://api.apify.com/v2/datasets/{r["defaultDatasetId"]}/items?token={AK}',timeout=60).json()
        log.append('items '+json.dumps(items)[:900])
        ok=grab(items)
        if not ok:
            lg=requests.get(f'https://api.apify.com/v2/actor-runs/{rid}/log?token={AK}',timeout=60).text
            log.append('LOG '+lg[-1200:])
    except Exception as e: log.append(f'run err {e!r}')
if not ok:
    subprocess.run('pip install -q -U yt-dlp',shell=True)
    for cl in ['android_vr','ios','tv_embedded']:
        r=subprocess.run(['yt-dlp','--extractor-args',f'youtube:player_client={cl}','-f','b[height<=720]/bv*[height<=720]+ba/b','--download-sections','*0-75','-o','/tmp/y.%(ext)s','--merge-output-format','mp4',url],capture_output=True,text=True)
        log.append(f'yt {cl} rc={r.returncode} '+r.stderr[-250:])
        if r.returncode==0 and os.path.exists('/tmp/y.mp4'): cut('/tmp/y.mp4'); ok=True; break
open('out/log.txt','w').write('\n'.join(log)); print('\n'.join(log))
