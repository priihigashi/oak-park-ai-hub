import os, json, subprocess, requests
os.makedirs('out/seg',exist_ok=True); log=[]
AK=os.environ['APIFY_API_KEY']
subprocess.run('pip install -q imageio-ffmpeg',shell=True)
import imageio_ffmpeg; FF=imageio_ffmpeg.get_ffmpeg_exe()
du=json.load(open('out/scan/src.json'))['url']
if 'token=' not in du: du+=('&' if '?' in du else '?')+'token='+AK
with requests.get(du,stream=True,timeout=900) as rr:
    with open('/tmp/v.mp4','wb') as f:
        for ch in rr.iter_content(1<<20): f.write(ch)
log.append(f'size {os.path.getsize("/tmp/v.mp4")}')
for name,a,d in [('A',1262,20),('B',1114,20)]:
    p=subprocess.run([FF,'-y','-ss',str(a),'-i','/tmp/v.mp4','-t',str(d),'-c:v','libx264','-crf','20','-preset','medium','-c:a','aac','-b:a','160k',f'out/seg/{name}.mp4'],capture_output=True,text=True); log.append(name+' rc '+str(p.returncode))
    subprocess.run([FF,'-y','-i',f'out/seg/{name}.mp4','-vf','fps=1,scale=240:-1,tile=5x4','-frames:v','1',f'out/seg/{name}_sheet.jpg'],capture_output=True)
log.append(str(os.listdir('out/seg')))
open('out/log.txt','w').write('\n'.join(log)); print('\n'.join(log))
