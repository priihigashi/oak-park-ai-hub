import os, json, re, subprocess, requests
os.makedirs('out/clip',exist_ok=True); log=[]
AK=os.environ.get('APIFY_API_KEY','')
vid='N6f6L80pXns'; url=f'https://www.youtube.com/watch?v={vid}'
def cut(src):
    p=subprocess.run(f'ffmpeg -y -i {src} -t 75 -c:v libx264 -preset veryfast -crf 24 -vf scale=-2:720 -c:a aac -b:a 160k out/clip/mae_raw.mp4',shell=True,capture_output=True,text=True); log.append('ff '+p.stderr[-300:])
ok=False
subprocess.run('pip install -q -U yt-dlp',shell=True)
for cl in ['android_vr','ios','tv_embedded','android']:
    r=subprocess.run(f'yt-dlp --extractor-args "youtube:player_client={cl}" -f "b[height<=720]/bv*[height<=720]+ba/b" --download-sections "*0-75" -o /tmp/y.%(ext)s --merge-output-format mp4 {url}',shell=True,capture_output=True,text=True)
    log.append(f'yt {cl} rc={r.returncode} '+r.stderr[-300:])
    if r.returncode==0 and os.path.exists('/tmp/y.mp4'): cut('/tmp/y.mp4'); ok=True; break
for actor,body in [('streamers~youtube-video-downloader',{"videos":[{"url":url}],"videoUrls":[{"url":url}],"preferredQuality":"720p","preferredFormat":"mp4"}),
                   ('epctex~youtube-video-downloader',{"startUrls":[url],"quality":"720","format":"mp4"}),
                   ('apilabs~youtube-downloader',{"url":url})]:
    if ok or not AK: break
    try:
        resp=requests.post(f'https://api.apify.com/v2/acts/{actor}/runs?token={AK}&waitForFinish=240',json=body,timeout=300).json()
        log.append(f'{actor} resp '+json.dumps(resp)[:400])
        rr=resp.get('data') or {}
        if not rr.get('defaultDatasetId'): continue
        items=requests.get(f'https://api.apify.com/v2/datasets/{rr["defaultDatasetId"]}/items?token={AK}',timeout=60).json()
        log.append('items '+json.dumps(items)[:800])
        for it in items:
            for k,v in it.items():
                if isinstance(v,str) and v.startswith('http') and 'youtube.com' not in v and ('mp4' in v or 'download' in k.lower() or 'googlevideo' in v or 'apify' in v):
                    try:
                        b=requests.get(v,timeout=300).content
                        if len(b)>200000: open('/tmp/a.mp4','wb').write(b); log.append(f'got {k} {len(b)}'); cut('/tmp/a.mp4'); ok=True; break
                    except Exception as e: log.append(f'dl err {e!r}')
            if ok: break
    except Exception as e: log.append(f'{actor} err {e!r}')
open('out/log.txt','w').write('\n'.join(log)); print('\n'.join(log))
