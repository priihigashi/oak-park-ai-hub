import os, subprocess, traceback
os.makedirs('out', exist_ok=True)
log=open('out/log.txt','w')
URL='https://www.instagram.com/reel/DfPnUwFBPiO/'
try:
    subprocess.run(['yt-dlp','-o','out/ref4.%(ext)s','-f','mp4/best',URL],timeout=300)
    vids=[f for f in os.listdir('out') if f.startswith('ref4.')]
    print('ig',vids,file=log)
    if vids:
        v='out/'+vids[0]
        from faster_whisper import WhisperModel
        m=WhisperModel('medium',compute_type='int8')
        segs,info=m.transcribe(v,language='pt')
        open('out/ref4_transcript.txt','w').write('\n'.join(f"[{s.start:.1f}] {s.text}" for s in segs))
        subprocess.run(['ffmpeg','-y','-i',v,'-vf','fps=1/4,scale=240:-2,tile=6x5','-frames:v','1','out/ref4_sheet.jpg'])
        subprocess.run(['ffmpeg','-y','-i',v,'-vf','scale=432:768,fps=24','-c:v','libx264','-preset','slow','-crf','32','-g','48','-pix_fmt','yuv420p','-c:a','aac','-b:a','64k','-ac','1','-movflags','+faststart','out/original4_leve.mp4'])
        os.remove(v)
except Exception: print(traceback.format_exc(),file=log)
log.close()
