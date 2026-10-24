import os, json, subprocess, urllib.request, urllib.parse, asyncio
J=json.load(open('job/job.json'))
os.makedirs('out',exist_ok=True)
def sh(c): print(c); subprocess.run(c,shell=True,check=True)
if J.get('video'):
    td=json.loads(os.environ['SHEETS_TOKEN'])
    tok=json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',data=urllib.parse.urlencode({'client_id':td['client_id'],'client_secret':td['client_secret'],'refresh_token':td['refresh_token'],'grant_type':'refresh_token'}).encode())).read())['access_token']
    url=f"https://www.googleapis.com/drive/v3/files/{J['video']}?alt=media&supportsAllDrives=true"
    with urllib.request.urlopen(urllib.request.Request(url,headers={'Authorization':'Bearer '+tok})) as r, open('orig.mp4','wb') as f:
        f.write(r.read())
    sh('ffprobe -v error -show_entries stream=width,height,r_frame_rate:format=duration orig.mp4')
    sh('ffmpeg -y -loglevel error -i orig.mp4 -vf "scale=540:-2,fps=30" -c:v libx264 -preset slow -crf 27 -g 15 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart out/work.mp4')
    sh('ffmpeg -y -loglevel error -i orig.mp4 -vf "scale=432:-2,fps=24" -c:v libx264 -preset slow -crf 32 -g 48 -pix_fmt yuv420p -c:a aac -b:a 64k -ac 1 -movflags +faststart out/original_leve.mp4')
    sh('ffmpeg -y -loglevel error -ss 1 -i out/original_leve.mp4 -frames:v 1 -q:v 4 out/original_leve.jpg')
    sh('ffmpeg -y -loglevel error -i orig.mp4 -ac 1 -ar 16000 a.wav')
    sh('for t in 2 20 50 90 120; do ffmpeg -y -loglevel error -ss $t -i orig.mp4 -frames:v 1 -vf scale=360:-2 out/f_$t.jpg; done')
    from faster_whisper import WhisperModel
    m=WhisperModel('medium',compute_type='int8')
    segs,_=m.transcribe('a.wav',language='pt',word_timestamps=True,vad_filter=False)
    words=[]
    for s in segs:
        for w in s.words: words.append({'w':w.word.strip(),'s':round(w.start,2),'e':round(w.end,2)})
    json.dump(words,open('out/words.json','w'),ensure_ascii=False)
if J.get('tts'):
    import edge_tts
    os.makedirs('out/vo',exist_ok=True)
    async def one(k,text,voice,rate):
        c=edge_tts.Communicate(text,voice,rate=rate,boundary='WordBoundary')
        b=[]; 
        with open(f'out/vo/{k}.mp3','wb') as f:
            async for ch in c.stream():
                if ch['type']=='audio': f.write(ch['data'])
                elif ch['type']=='WordBoundary': b.append({'w':ch['text'],'s':ch['offset']/1e7,'e':(ch['offset']+ch['duration'])/1e7})
        json.dump(b,open(f'out/vo/{k}.json','w'),ensure_ascii=False)
    async def main():
        for k,t in J['tts'].items():
            for v,rt in [(J.get('voice','pt-BR-ThalitaMultilingualNeural'),J.get('rate','+12%')),('pt-BR-ThalitaNeural','+12%'),('pt-BR-FranciscaNeural','+12%'),('pt-BR-AntonioNeural','+12%')]:
                try:
                    await one(k,t,v,rt); print(k,'voice',v); open('out/vo/voice.txt','w').write(v); break
                except Exception as ex: print(k,v,'fail',ex)
    asyncio.run(main())
if J.get('heads'):
    sh('pip install -q "rembg[cpu]" mediapipe==0.10.14 opencv-python-headless pillow')
    import requests, numpy as np, cv2
    from PIL import Image
    from rembg import remove, new_session
    import mediapipe as mp
    os.makedirs('out/heads',exist_ok=True)
    sess=new_session('isnet-general-use')
    for k,title in J['heads'].items():
        try:
            meta=requests.get('https://pt.wikipedia.org/api/rest_v1/page/summary/'+title,headers={'User-Agent':'tmp-bot/1.0'}).json()
            url=meta.get('originalimage',{}).get('source') or meta['thumbnail']['source']
            img=Image.open(__import__('io').BytesIO(requests.get(url,headers={'User-Agent':'tmp-bot/1.0'}).content)).convert('RGB')
            if img.width>1400: img=img.resize((1400,int(img.height*1400/img.width)))
            img.save(f'out/heads/{k}_src.jpg')
            cut=remove(img,session=sess,alpha_matting=True,alpha_matting_foreground_threshold=240,alpha_matting_background_threshold=10,alpha_matting_erode_size=10)
            a=np.array(cut); H,Wd=a.shape[:2]
            fm=mp.solutions.face_mesh.FaceMesh(static_image_mode=True,max_num_faces=1)
            res=fm.process(np.array(img))
            lm=res.multi_face_landmarks[0].landmark
            P=lambda i:(lm[i].x*Wd,lm[i].y*H)
            chin=P(152); L=P(234); R=P(454); top=P(10)
            fh=chin[1]-top[1]; cy=chin[1]+0.05*fh
            mask=np.zeros((H,Wd),np.uint8)
            # keep above jaw: polygon from jaw landmarks
            jaw=[234,93,132,58,172,136,150,149,176,148,152,377,400,378,379,365,397,288,361,323,454]
            pts=[P(i) for i in jaw]
            pts=[(x,y+0.05*fh) for x,y in pts]
            poly=[(0,0),(0,pts[0][1])]+pts+[(Wd,pts[-1][1]),(Wd,0)]
            cv2.fillPoly(mask,[np.array(poly,np.int32)],255)
            mask=cv2.GaussianBlur(mask,(5,5),0)
            a[...,3]=(a[...,3].astype(np.float32)*mask/255).astype(np.uint8)
            ys,xs=np.where(a[...,3]>20); a=a[ys.min():ys.max()+1,xs.min():xs.max()+1]
            Image.fromarray(a).save(f'out/heads/{k}.png'); print('head ok',k,a.shape)
        except Exception as ex: print('head fail',k,ex)

if J.get('drive'):
    import mimetypes
    td=json.loads(os.environ['SHEETS_TOKEN'])
    tok=json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',data=urllib.parse.urlencode({'client_id':td['client_id'],'client_secret':td['client_secret'],'refresh_token':td['refresh_token'],'grant_type':'refresh_token'}).encode())).read())['access_token']
    import requests
    H={'Authorization':'Bearer '+tok}
    def mkdir(name,parent):
        r=requests.post('https://www.googleapis.com/drive/v3/files?supportsAllDrives=true&fields=id',headers=H,json={'name':name,'mimeType':'application/vnd.google-apps.folder','parents':[parent]}); r.raise_for_status(); return r.json()['id']
    def up(path,parent,name=None):
        meta={'name':name or os.path.basename(path),'parents':[parent]}
        mt=mimetypes.guess_type(path)[0] or 'application/octet-stream'
        r=requests.post('https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&supportsAllDrives=true&fields=id',headers={**H,'Content-Type':'application/json; charset=UTF-8','X-Upload-Content-Type':mt},json=meta); r.raise_for_status()
        r2=requests.put(r.headers['Location'],data=open(path,'rb'),headers={'Content-Type':mt}); r2.raise_for_status(); return r2.json()['id']
    D=J['drive']; res={}
    v=mkdir(D['folder'],D['parent']); res['folder']=v
    sub={k:mkdir(k,v) for k in ['motion','png','resources']}; res.update({'sub_'+k:i for k,i in sub.items()})
    for f in D['files']:
        res[f['name']]=up(f['path'],sub[f['sub']],f['name'])
    for f in D.get('public',[]):
        res['pub_'+f['name']]=up(f['path'],D['public_folder'],f['name'])
    os.makedirs('out',exist_ok=True); json.dump(res,open('out/drive.json','w'),indent=1); print(res)

if J.get('mark'):
    import requests
    from faster_whisper import WhisperModel
    os.makedirs('out/mark',exist_ok=True)
    m=WhisperModel('medium',compute_type='int8')
    for k,u in J['mark'].items():
        open(f'raw_{k}.mp3','wb').write(requests.get(u).content)
        sh(f'ffmpeg -y -loglevel error -i raw_{k}.mp3 -af "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,atempo=1.2" -ar 44100 -ac 1 -b:a 128k out/mark/{k}.mp3')
        segs,_=m.transcribe(f'out/mark/{k}.mp3',language='pt',word_timestamps=True,initial_prompt=J['text'][k])
        words=[{'w':w.word.strip(),'s':round(w.start,3),'e':round(w.end,3)} for s in segs for w in s.words]
        json.dump(words,open(f'out/mark/{k}.json','w'),ensure_ascii=False)
