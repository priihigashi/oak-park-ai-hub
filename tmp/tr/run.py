import os, json, subprocess, base64, urllib.request, urllib.parse, glob, pathlib
OUT=pathlib.Path('tmp/tr/out'); OUT.mkdir(parents=True, exist_ok=True)
URL="https://www.instagram.com/reel/De4uxy0xC1m/"
FOLDER="1dZil2rvx6ak-en1YdLOoksxPcWLkooRO"
blob=os.environ.get('PRI_OP_IG_COOKIES','')
ck='/tmp/ig.txt'
if blob:
    try:
        d=base64.b64decode(blob,validate=True)
        open(ck,'wb').write(d if (b'\n' in d or b'\t' in d) else blob.encode())
    except Exception: open(ck,'w').write(blob)
log=[]
def dl(args):
    r=subprocess.run(['yt-dlp','-f','best[ext=mp4]/best','-o',str(OUT/'reel.%(ext)s'),'--write-info-json','--no-playlist']+args+[URL],capture_output=True,text=True)
    log.append(r.stdout[-1500:]+r.stderr[-1500:]); return r.returncode==0
ok = (blob and dl(['--cookies',ck])) or dl([])
open(OUT/'log.txt','w').write('\n----\n'.join(log))
vids=[f for f in glob.glob(str(OUT/'reel.*')) if not f.endswith('.json')]
if not vids: raise SystemExit('download failed')
v=vids[0]
subprocess.run(['ffmpeg','-y','-i',v,'-vf','scale=-2:960','-c:v','libx264','-crf','30','-preset','veryfast','-c:a','aac','-b:a','96k',str(OUT/'reel_small.mp4')],check=True)
subprocess.run(['ffmpeg','-y','-i',v,'-ac','1','-ar','16000','/tmp/a.wav'],check=True)
(OUT/'frames').mkdir(exist_ok=True)
subprocess.run(['ffmpeg','-y','-i',v,'-vf','fps=1/2,scale=360:-2',str(OUT/'frames/f_%03d.jpg')],check=True)
from faster_whisper import WhisperModel
m=WhisperModel('medium',device='cpu',compute_type='int8')
segs,info=m.transcribe('/tmp/a.wav',language='pt',word_timestamps=True,vad_filter=False,beam_size=5)
lines=[];words=[]
for s in segs:
    lines.append(f"[{int(s.start//60):02d}:{s.start%60:05.2f}] {s.text.strip()}")
    for w in (s.words or []): words.append({'w':w.word,'s':round(w.start,2),'e':round(w.end,2)})
info_j={}
try: info_j=json.load(open(glob.glob(str(OUT/'reel*.info.json'))[0]))
except Exception: pass
head=f"TRANSCRIÇÃO COMPLETA — reel {URL}\nPerfil: @{info_j.get('uploader_id') or info_j.get('channel') or ''} ({info_j.get('uploader','')})\nData: {info_j.get('upload_date','')}  Duração: {info_j.get('duration','')} s\nLegenda do post: {info_j.get('description','')}\nTranscrição automática (faster-whisper medium), revisar nomes próprios.\n\n"
txt=head+'\n'.join(lines)
open(OUT/'transcricao.txt','w').write(txt)
json.dump(words,open(OUT/'words.json','w'),ensure_ascii=False)
json.dump({k:info_j.get(k) for k in ['uploader','uploader_id','channel','upload_date','duration','description','like_count','comment_count','view_count','title']},open(OUT/'meta.json','w'),ensure_ascii=False,indent=1)
for f in glob.glob(str(OUT/'reel*.info.json')): os.remove(f)
os.remove(v) if os.path.getsize(v)>40e6 else None
# Drive upload
td=json.loads(os.environ['SHEETS_TOKEN'])
tok=json.loads(urllib.request.urlopen('https://oauth2.googleapis.com/token',urllib.parse.urlencode({'client_id':td['client_id'],'client_secret':td['client_secret'],'refresh_token':td['refresh_token'],'grant_type':'refresh_token'}).encode()).read())['access_token']
def up(path,name,mime):
    meta=json.dumps({'name':name,'parents':[FOLDER]}).encode()
    b='xxBOUNDARYxx'
    body=b'--'+b.encode()+b'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'+meta+b'\r\n--'+b.encode()+f'\r\nContent-Type: {mime}\r\n\r\n'.encode()+open(path,'rb').read()+b'\r\n--'+b.encode()+b'--'
    req=urllib.request.Request('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true&fields=id,name,parents',data=body,headers={'Authorization':'Bearer '+tok,'Content-Type':'multipart/related; boundary='+b})
    return json.loads(urllib.request.urlopen(req).read())
res={'transcricao':up(str(OUT/'transcricao.txt'),'TRANSCRICAO_reel_triplex_rachadinha.txt','text/plain'),
     'video':up(str(OUT/'reel_small.mp4'),'REEL_original_triplex_rachadinha.mp4','video/mp4')}
json.dump(res,open(OUT/'drive.json','w'),indent=1)
print(res)
