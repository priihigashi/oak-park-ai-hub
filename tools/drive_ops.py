import json,os,glob
job=json.load(open('job.json')); ops=job.get('drive_ops')
if not ops: raise SystemExit(0)
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
info=json.loads(os.environ['SHEETS_TOKEN']); creds=Credentials.from_authorized_user_info(info,info.get('scopes'))
d=build('drive','v3',credentials=creds); out={}
def folder(name,parent):
    q=f"name='{name}' and '{parent}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    r=d.files().list(q=q,supportsAllDrives=True,includeItemsFromAllDrives=True,fields='files(id)').execute()['files']
    if r: return r[0]['id']
    return d.files().create(body={'name':name,'mimeType':'application/vnd.google-apps.folder','parents':[parent]},supportsAllDrives=True,fields='id').execute()['id']
for op in ops:
    try:
        if op['op']=='move':
            f=d.files().get(fileId=op['id'],fields='parents',supportsAllDrives=True).execute()
            d.files().update(fileId=op['id'],addParents=op['to'],removeParents=','.join(f.get('parents',[])),supportsAllDrives=True).execute(); out[op['id']]='moved'
        elif op['op']=='trash':
            d.files().update(fileId=op['id'],body={'trashed':True},supportsAllDrives=True).execute(); out[op['id']]='trashed'
        elif op['op']=='faces':
            t=folder('Templates',op['root']); fz=folder('Faces',t); n=0
            have={x['name'] for x in d.files().list(q=f"'{fz}' in parents and trashed=false",supportsAllDrives=True,includeItemsFromAllDrives=True,pageSize=500,fields='files(name)').execute()['files']}
            for p in sorted(glob.glob('out/faces/*.png')):
                nm=os.path.basename(p)
                if nm in have: continue
                d.files().create(body={'name':nm,'parents':[fz]},media_body=MediaFileUpload(p,mimetype='image/png'),supportsAllDrives=True,fields='id').execute(); n+=1
            out['faces']={'folder':fz,'uploaded':n}
        elif op['op']=='sheet_append':
            s=build('sheets','v4',credentials=creds)
            meta=s.spreadsheets().get(spreadsheetId=op['sheet']).execute()
            tabs=[x['properties']['title'] for x in meta['sheets']]; out['tabs']=tabs
            tab=next((x for x in tabs if op['tab_contains'] in x),None); out['tab']=tab
            if tab:
                hdr=s.spreadsheets().values().get(spreadsheetId=op['sheet'],range=f"'{tab}'!1:1").execute().get('values',[[]])[0]; out['hdr']=hdr
                for row in op['rows']:
                    vals=[]
                    for h in hdr:
                        hl=h.lower(); v=''
                        for k,val in row.items():
                            if any(w in hl for w in k.split('|')): v=val; break
                        vals.append(v)
                    s.spreadsheets().values().append(spreadsheetId=op['sheet'],range=f"'{tab}'!A1",valueInputOption='USER_ENTERED',insertDataOption='INSERT_ROWS',body={'values':[vals]}).execute()
                out['appended']=len(op['rows'])
    except Exception as e: out[str(op)[:80]]='ERR '+repr(e)[:300]
print('DRIVE_OPS',json.dumps(out,ensure_ascii=False))
