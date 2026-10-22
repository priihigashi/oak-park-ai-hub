import os, json, subprocess, requests, time
os.makedirs('out/scan',exist_ok=True); log=[]
AK=os.environ['APIFY_API_KEY']; url='https://www.youtube.com/watch?v=N6f6L80pXns'
subprocess.run('pip install -q imageio-ffmpeg',shell=True)
import imageio_ffmpeg; FF=imageio_ffmpeg.get_ffmpeg_exe()
r=requests.post(f'https://api.apify.com/v2/acts/epctex~youtube-video-downloader/runs?token={AK}',json={"startUrls":[url],"quality":"1080","format":"mp4"},timeout=60).json()['data']
rid=r['id']; log.append('run '+rid)
for _ in range(80):
    r=requests.get(f'https://api.apify.com/v2/actor-runs/{rid}?token={AK}',timeout=60).json()['data']
    if r['status'] not in ('READY','RUNNING'): break
    time.sleep(10)
log.append(r['status'])
items=requests.get(f'https://api.apify.com/v2/datasets/{r["defaultDatasetId"]}/items?token={AK}',timeout=60).json()
log.append(json.dumps(items)[:500])
du=items[0]['output']['url']
json.dump({'url':du,'run':rid},open('out/scan/src.json','w'))
with requests.get(du,stream=True,timeout=900) as rr:
    with open('/tmp/v.mp4','wb') as f:
        for ch in rr.iter_content(1<<20): f.write(ch)
log.append(f'size {os.path.getsize("/tmp/v.mp4")}')
p=subprocess.run([FF,'-i','/tmp/v.mp4'],capture_output=True,text=True); log.append(p.stderr[-600:])
subprocess.run([FF,'-y','-i','/tmp/v.mp4','-vf','fps=1/3,scale=256:-1,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text=%{pts\\:hms}:x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black,tile=8x8','out/scan/sheet_%02d.jpg'],capture_output=True)
log.append('sheets '+str(sorted(os.listdir('out/scan'))))
open('out/log.txt','w').write('\n'.join(log)); print('\n'.join(log))
