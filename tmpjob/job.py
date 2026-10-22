import os, json, re, subprocess, requests, time
os.makedirs('out/clip',exist_ok=True); log=[]
SK=os.environ.get('SERP_API_KEY',''); AK=os.environ.get('APIFY_API_KEY','')
hit=None
for vid in ['N6f6L80pXns','j4cghMn_i_k']:
    try:
        r=requests.get('https://serpapi.com/search.json',params={'engine':'youtube_video_transcript','v':vid,'language_code':'pt','api_key':SK},timeout=90).json()
        tr=r.get('transcript') or []
        log.append(f'{vid} transcript {len(tr)} keys {list(r.keys())[:8]}')
        json.dump(tr,open(f'out/clip/{vid}_tr.json','w'),ensure_ascii=False)
        for i,s in enumerate(tr):
            if re.search('vingan',s.get('snippet',''),re.I):
                hit=(vid,s['start_ms']/1000); log.append(f'HIT {vid} {s}'); break
        if hit: break
    except Exception as e: log.append(f'serp err {vid} {e!r}')
if hit and AK:
    vid,t=hit; url=f'https://www.youtube.com/watch?v={vid}'
    for actor,body in [('streamers~youtube-video-downloader',{"videoUrls":[{"url":url}],"url":url,"format":"mp4","quality":"360p","resolution":"360p"})]:
        try:
            rr=requests.post(f'https://api.apify.com/v2/acts/{actor}/runs?token={AK}&waitForFinish=280',json=body,timeout=320).json()['data']
            log.append(f'apify {actor} {rr.get("status")}')
            items=requests.get(f'https://api.apify.com/v2/datasets/{rr["defaultDatasetId"]}/items?token={AK}',timeout=60).json()
            log.append('items '+json.dumps(items)[:600])
            du=''
            for it in items:
                du=it.get('downloadUrl') or it.get('url') or it.get('videoUrl') or it.get('link') or ''
                if du and 'youtube.com/watch' not in du: break
            if du:
                b=requests.get(du,timeout=300).content; open('/tmp/full.mp4','wb').write(b); log.append(f'full {len(b)}')
                a=max(0,t-30)
                p=subprocess.run(f'ffmpeg -y -ss {a} -i /tmp/full.mp4 -t 60 -c:v libx264 -preset veryfast -crf 26 -vf scale=-2:540 -c:a aac -b:a 128k out/clip/mae_raw.mp4',shell=True,capture_output=True,text=True)
                log.append('ff '+p.stderr[-300:]); json.dump({'vid':vid,'t':t,'a':a},open('out/clip/info.json','w'))
                break
        except Exception as e: log.append(f'apify err {e!r}')
open('out/log.txt','w').write('\n'.join(log)); print('\n'.join(log))
