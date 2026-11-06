# rerun v1c
import subprocess,sys,json,os,glob
import numpy as np
subprocess.run([sys.executable,'-m','pip','install','-q','edge-tts==7.3.1'])
os.makedirs('asr',exist_ok=True)
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
def load(p):
    raw=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',p,'-f','s16le','-ac','1','-ar','16000','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.int16).astype(np.float32)/32768.0
for f in sorted(glob.glob('tts/*.mp3')):
    n=os.path.basename(f)[:-4]; segs,_=m.transcribe(load(f),language='pt')
    open(f'asr/back_{n}.txt','w').write(' '.join(s.text for s in segs))
