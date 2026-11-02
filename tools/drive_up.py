import json,os,glob,subprocess
job=json.load(open('job.json')); up=job.get('upload')
if not up: raise SystemExit(0)
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
info=json.loads(os.environ['SHEETS_TOKEN']); creds=Credentials.from_authorized_user_info(info,info.get('scopes'))
d=build('drive','v3',credentials=creds); res={}
for name,spec in up['files'].items():
    if spec.get('parts'):
        parts=sorted(glob.glob(spec['parts']))
        with open('/tmp/'+name,'wb') as o:
            for p in parts: o.write(open(p,'rb').read())
        path='/tmp/'+name
    else: path=spec['path']
    f=d.files().create(body={'name':name,'parents':[up['folder']]},media_body=MediaFileUpload(path,mimetype=spec['mime'],resumable=True),supportsAllDrives=True,fields='id,name,size,webViewLink').execute()
    res[name]=f; print(f)
os.makedirs('out/upload',exist_ok=True); json.dump(res,open('out/upload/ids.json','w'),indent=1)
