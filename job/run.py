import json, os, subprocess, asyncio, re, sys, traceback
J=json.load(open('job/script.json')); O='out'; os.makedirs(O,exist_ok=True)
log=open(f'{O}/log.txt','w')
def L(*a):
    print(*a); print(*a,file=log); log.flush()
def sh(c):
    L('$',c); r=subprocess.run(c,shell=True,capture_output=True,text=True); L(r.stdout[-1500:],r.stderr[-1500:]); return r.returncode
# 1 TTS
import edge_tts
async def tts(sc):
    com=edge_tts.Communicate(sc['text'],J['voice'],rate=J['rate'],boundary='WordBoundary')
    words=[]; 
    with open(f"{O}/{sc['id']}.mp3",'wb') as f:
        async for ch in com.stream():
            if ch['type']=='audio': f.write(ch['data'])
            elif ch['type']=='WordBoundary': words.append([ch['text'],ch['offset']/1e7,(ch['offset']+ch['duration'])/1e7])
    json.dump(words,open(f"{O}/{sc['id']}.json",'w'),ensure_ascii=False)
for sc in J['scenes']:
    try: asyncio.run(tts(sc)); L('tts ok',sc['id'])
    except Exception as e: L('tts fail',sc['id'],traceback.format_exc())
# 2 video
ok=sh(f"yt-dlp -f 'bv*+ba/b' --merge-output-format mp4 -o orig.mp4 '{J['reel']}'")==0 and os.path.exists('orig.mp4')
if not ok:
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
        tok=os.environ.get('SHEETS_TOKEN','')
        open('tok.json','w').write(tok)
        cr=Credentials.from_authorized_user_file('tok.json')
        d=build('drive','v3',credentials=cr)
        req=d.files().get_media(fileId=J['drive_file_id'],supportsAllDrives=True)
        import io; fh=io.FileIO('orig.mp4','wb'); dl=MediaIoBaseDownload(fh,req)
        done=False
        while not done: _,done=dl.next_chunk()
        L('drive ok')
    except Exception: L('drive fail',traceback.format_exc())
if os.path.exists('orig.mp4'):
    sh("ffprobe -v error -show_entries stream=width,height,r_frame_rate,codec_type -show_entries format=duration -of json orig.mp4 > out/probe.json")
    sh("ffmpeg -y -ss 0 -t 4.2 -i orig.mp4 -vf 'scale=540:960:force_original_aspect_ratio=increase,crop=540:960,fps=30' -c:v libx264 -crf 27 -g 15 -pix_fmt yuv420p -an -movflags +faststart out/c1_raw.mp4")
    sh("ffmpeg -y -ss 0 -t 4.2 -i orig.mp4 -vn -af 'highpass=f=90,acompressor,loudnorm=I=-13' -ar 44100 -ac 1 out/c1.wav")
    sh("ffmpeg -y -i orig.mp4 -vf scale=432:768,fps=24 -c:v libx264 -preset slow -crf 32 -g 48 -pix_fmt yuv420p -c:a aac -b:a 64k -ac 1 -movflags +faststart out/original_leve.mp4")
    sh("ffmpeg -y -ss 1 -i orig.mp4 -frames:v 1 -vf scale=432:768 out/original_poster.jpg")
    for i,t in enumerate([0.5,1.5,2.5,3.5,6,20,40,60,80,88]):
        sh(f"ffmpeg -y -ss {t} -i orig.mp4 -frames:v 1 -vf scale=360:640 out/fr_{i:02d}.jpg")
    try:
        from faster_whisper import WhisperModel
        m=WhisperModel('medium',device='cpu',compute_type='int8')
        segs,_=m.transcribe('out/c1.wav',language='pt',word_timestamps=True)
        w=[[x.word.strip(),x.start,x.end] for s in segs for x in s.words]
        json.dump(w,open('out/c1_words.json','w'),ensure_ascii=False); L('whisper ok',w)
    except Exception: L('whisper fail',traceback.format_exc())
# 3 photos
import requests
from bs4 import BeautifulSoup
H={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
os.makedirs(f'{O}/ph',exist_ok=True); n=0
for u in J['photo_pages']:
    try:
        r=requests.get(u,headers=H,timeout=25); s=BeautifulSoup(r.text,'html.parser')
        cands=[m.get('content') for m in s.find_all('meta') if m.get('property') in ('og:image','twitter:image') or m.get('name') in ('twitter:image',)]
        cands+= [i.get('src') for i in s.select('article img, figure img') if i.get('src','').startswith('http')][:4]
        seen=set()
        for c in cands:
            if not c or c in seen: continue
            seen.add(c)
            try:
                ir=requests.get(c,headers=H,timeout=25)
                if ir.ok and len(ir.content)>15000:
                    ext='jpg' if 'png' not in c.lower() else 'png'
                    open(f'{O}/ph/p{n:02d}.{ext}','wb').write(ir.content); L('photo',n,u,c); n+=1
            except Exception as e: L('img fail',c,e)
    except Exception as e: L('page fail',u,e)
# 4 cutouts
try:
    from rembg import remove, new_session
    ses=new_session('isnet-general-use')
    from PIL import Image
    os.makedirs(f'{O}/cut',exist_ok=True)
    for f in sorted(os.listdir(f'{O}/ph')):
        try:
            im=Image.open(f'{O}/ph/{f}').convert('RGB')
            if max(im.size)>1600: im.thumbnail((1600,1600))
            res=remove(im,session=ses,alpha_matting=True,alpha_matting_foreground_threshold=240,alpha_matting_background_threshold=10,alpha_matting_erode_size=10)
            res.save(f'{O}/cut/{f.rsplit(".",1)[0]}.png'); L('cut',f)
        except Exception: L('cut fail',f,traceback.format_exc())
except Exception: L('rembg fail',traceback.format_exc())
L('DONE')
