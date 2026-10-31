import json, os, subprocess, glob
job=json.load(open('job.json')); reels=job.get('reels',[])
os.makedirs('out/ref',exist_ok=True)
ck=os.environ.get('PRI_OP_IG_COOKIES','')
if ck: open('/tmp/ig.txt','w').write(ck)
res={}
def save(): json.dump(res,open('out/ref/log.json','w'),indent=1)
for r in reels:
    res[r]={}
    for url in [f'https://www.instagram.com/reel/{r}/', f'https://www.instagram.com/p/{r}/']:
        if glob.glob(f'out/ref/{r}.mp4'): break
        cmd=['yt-dlp','-v','-f','b[height<=720]/b/bv*+ba','--merge-output-format','mp4','-o',f'out/ref/{r}.%(ext)s','--write-info-json',url]
        if ck: cmd[1:1]=['--cookies','/tmp/ig.txt']
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=300); res[r]['log_'+url[-14:]]=(p.stdout+p.stderr)[-1500:]
    save()
    vids=glob.glob(f'out/ref/{r}.mp4')
    if not vids: continue
    v=vids[0]
    res[r]['dur']=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',v],capture_output=True,text=True).stdout.strip()
    subprocess.run(['ffmpeg','-v','error','-y','-i',v,'-vf','fps=1/3,scale=200:-1,tile=8x8','-frames:v','1',f'out/ref/{r}_sheet.jpg'])
    subprocess.run(['ffmpeg','-v','error','-y','-i',v,'-ac','1','-ar','16000',f'/tmp/{r}.wav'])
    save()
    try:
        from faster_whisper import WhisperModel
        m=WhisperModel('base',compute_type='int8')
        segs,_=m.transcribe(f'/tmp/{r}.wav',language='pt')
        open(f'out/ref/{r}.txt','w').write('\n'.join(f'[{s.start:.1f}-{s.end:.1f}] {s.text.strip()}' for s in segs))
    except Exception as e: res[r]['wh']=str(e)
    save()
    if os.path.getsize(v)>15e6:
        subprocess.run(['ffmpeg','-v','error','-y','-i',v,'-vf','scale=360:-2','-b:v','500k','-b:a','64k',f'/tmp/{r}_s.mp4']); os.replace(f'/tmp/{r}_s.mp4',v)
