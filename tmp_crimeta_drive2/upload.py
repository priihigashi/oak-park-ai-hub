import json,os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
info=json.loads(os.environ['SHEETS_TOKEN'])
c=Credentials.from_authorized_user_info(info,info.get('scopes'))
if not c.valid: c.refresh(Request())
d=build('drive','v3',credentials=c);B='tmp_crimeta_drive2';rep={}
for f,fid,mt in [('reel_crimeta-russa_v2.mp4','1IJkhhBgrDAsMjQ-m1SYeA6U5HVf1sCv2','video/mp4'),('render_s1spin.py','1Inp5vxBrHswnkSYR3dmGPwvmT9ocXdYK','text/x-python'),('spin.py','1Inp5vxBrHswnkSYR3dmGPwvmT9ocXdYK','text/x-python')]:
    rep[f]=d.files().create(body={'name':f,'parents':[fid]},media_body=MediaFileUpload(f'{B}/{f}',mimetype=mt,resumable=True),supportsAllDrives=True,fields='id,size').execute()
note="\nNOTE — 2026-10-22 (2)\n- Reel v2 (reel_crimeta-russa_v2.mp4, 47,6 s): a roleta do card 1 gira 2 vezes com barulhinho de roleta (tic a cada casa + ding quando para), card 1 dura 7,6 s, depois vídeo do vizinho e card da checagem. Pra postar como reel de teste em 23/10.\n"
try:
    docs=build('docs','v1',credentials=c);DID='1lrkMtUyXwOK8rCtWUCU5lj7yIlm_z54DpySUhCQ5Obw'
    end=docs.documents().get(documentId=DID).execute()['body']['content'][-1]['endIndex']-1
    docs.documents().batchUpdate(documentId=DID,body={'requests':[{'insertText':{'location':{'index':end},'text':note}}]}).execute();rep['note']='ok'
except Exception as e: rep['note']='fail: '+str(e)[:200]
os.makedirs(f'{B}/out',exist_ok=True);json.dump(rep,open(f'{B}/out/report.json','w'),indent=1)
print(rep)
