import json, os, subprocess
job=json.load(open('job.json')); reels=job.get('reels',[])
os.makedirs('out/ref',exist_ok=True)
ck=os.environ.get('PRI_OP_IG_COOKIES','')
if ck: open('/tmp/ig.txt','w').write(ck)
res={}
for r in reels:
    url=f'https://www.instagram.com/reel/{r}/'
    cmd=['yt-dlp','-f','best[height<=480]/worst','-o',f'out/ref/{r}.%(ext)s','--write-info-json',url]
    if ck: cmd[1:1]=['--cookies','/tmp/ig.txt']
    p=subprocess.run(cmd,capture_output=True,text=True); res[r]={'log':(p.stdout+p.stderr)[-800:]}
    vids=[f for f in os.listdir('out/ref') if f.startswith(r) and f.endswith(('.mp4','.webm','.mkv'))]
    if vids:
        v='out/ref/'+vids[0]
        d=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',v],capture_output=True,text=True).stdout.strip()
        res[r]['dur']=d
        try:
            from faster_whisper import WhisperModel
            m=WhisperModel('small',compute_type='int8')
            segs,_=m.transcribe(v,language='pt')
            open(f'out/ref/{r}.txt','w').write('\n'.join(f'[{s.start:.1f}-{s.end:.1f}] {s.text.strip()}' for s in segs))
        except Exception as e: res[r]['wh']=str(e)
        subprocess.run(['ffmpeg','-v','error','-y','-i',v,'-vf','fps=1/3,scale=240:-1,tile=6x4','-frames:v','1',f'out/ref/{r}_sheet.jpg'])
json.dump(res,open('out/ref/log.json','w'),indent=1)
