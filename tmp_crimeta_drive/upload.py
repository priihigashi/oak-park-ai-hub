import json,os,mimetypes
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
info=json.loads(os.environ['SHEETS_TOKEN'])
c=Credentials.from_authorized_user_info(info,info.get('scopes'))
if not c.valid: c.refresh(Request())
d=build('drive','v3',credentials=c)
F={'png':'1m8L936HyeNtyQXso_1TJOW_CLW4YzcLG','motion':'1IJkhhBgrDAsMjQ-m1SYeA6U5HVf1sCv2','resources':'1Inp5vxBrHswnkSYR3dmGPwvmT9ocXdYK'}
V='1HQcLbuSbym5Ud8MQPv5haytv5F2An76L'
B='tmp_crimeta_drive'
rep={}
for sub,fid in F.items():
    for f in sorted(os.listdir(f'{B}/{sub}')):
        p=f'{B}/{sub}/{f}';mt=mimetypes.guess_type(f)[0] or 'application/octet-stream'
        r=d.files().create(body={'name':f,'parents':[fid]},media_body=MediaFileUpload(p,mimetype=mt,resumable=True),supportsAllDrives=True,fields='id,name,size').execute()
        rep[f'{sub}/{f}']=r
r=d.files().create(body={'name':'story · Crimeta Russa v1','mimeType':'application/vnd.google-apps.document','parents':[V]},media_body=MediaFileUpload(f'{B}/story.md',mimetype='text/plain'),supportsAllDrives=True,fields='id,name').execute()
rep['story']=r
os.makedirs(f'{B}/out',exist_ok=True);json.dump(rep,open(f'{B}/out/report.json','w'),indent=1,ensure_ascii=False)
print(json.dumps(rep,ensure_ascii=False))
