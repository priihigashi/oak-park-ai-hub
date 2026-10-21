import glob,json,os,sys
from faster_whisper import WhisperModel
D=sys.argv[1]; m=WhisperModel('medium',device='cpu',compute_type='int8')
for f in sorted(glob.glob(f'{D}/out/vid/*.mp4')):
    if os.path.exists(f[:-4]+'.asr.json'): continue
    segs,info=m.transcribe(f,language='pt',word_timestamps=True,vad_filter=True)
    out=[]
    for s in segs: out.append({'s':round(s.start,2),'e':round(s.end,2),'t':s.text,'w':[[w.word,round(w.start,2),round(w.end,2)] for w in (s.words or [])]})
    json.dump(out,open(f[:-4]+'.asr.json','w'),ensure_ascii=False)
    print(os.path.basename(f), ' '.join(x['t'] for x in out)[:400])
