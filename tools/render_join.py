import json,os,glob,subprocess
J=json.load(open('render_job.json'))
parts=sorted(glob.glob('chunks/chunk-*/chunk.mp4'),key=lambda p:int(p.split('chunk-')[1].split('/')[0]))
open('l.txt','w').write(''.join(f"file '{p}'\n" for p in parts))
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i','l.txt','-i','render_src/'+J['audio'],'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',J['name']],check=True)
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
info=json.loads(os.environ['SHEETS_TOKEN']); creds=Credentials.from_authorized_user_info(info,info.get('scopes'))
d=build('drive','v3',credentials=creds)
f=d.files().create(body={'name':J['name'],'parents':[J['folder']]},media_body=MediaFileUpload(J['name'],mimetype='video/mp4',resumable=True),supportsAllDrives=True,fields='id,name,size,webViewLink').execute()
print('UPLOADED',json.dumps(f))
