import subprocess,sys,json,os,glob
import numpy as np
subprocess.run([sys.executable,'-m','pip','install','-q','edge-tts==7.3.1'])
os.makedirs('asr',exist_ok=True)
subprocess.run([sys.executable,'tts.py','pt-BR-ThalitaMultilingualNeural'],check=False)
os.makedirs('asr/tts',exist_ok=True)
for f in glob.glob('tts/*'): subprocess.run(['cp',f,'asr/tts/'])
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
def load(p):
    raw=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',p,'-f','s16le','-ac','1','-ar','16000','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.int16).astype(np.float32)/32768.0
def tr(path,name):
    segs,_=m.transcribe(load(path),language='pt',word_timestamps=True)
    out={'segments':[],'words':[]}
    for s in segs:
        out['segments'].append([round(s.start,2),round(s.end,2),s.text])
        out['words']+=[[w.word,round(w.start,2),round(w.end,2)] for w in s.words]
    json.dump(out,open(f'asr/{name}.json','w'),ensure_ascii=False,indent=0)
tr('clips/flavio_recife.mp4','flavio_recife')
for f in sorted(glob.glob('tts/*.mp3')):
    n=os.path.basename(f)[:-4]; segs,_=m.transcribe(load(f),language='pt')
    open(f'asr/back_{n}.txt','w').write(' '.join(s.text for s in segs))
