import os,json,urllib.request,urllib.parse,zipfile,shutil,subprocess
td=json.loads(os.environ['SHEETS_TOKEN'])
tok=json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',data=urllib.parse.urlencode({'client_id':td['client_id'],'client_secret':td['client_secret'],'refresh_token':td['refresh_token'],'grant_type':'refresh_token'}).encode())).read())['access_token']
FID='1RZ01LQDhxJvc7cW2nCu8VPdK_QC5kf4t'
with urllib.request.urlopen(urllib.request.Request(f'https://www.googleapis.com/drive/v3/files/{FID}?alt=media&supportsAllDrives=true',headers={'Authorization':'Bearer '+tok})) as r: open('kit.zip','wb').write(r.read())
shutil.rmtree('kx',ignore_errors=True); zipfile.ZipFile('kit.zip').extractall('kx')
subprocess.run(['python','job/patch_kit.py','kx/kit'],check=True)
shutil.copy('job/SKILL.md','kx/kit/SKILL.md')
os.remove('kit.zip')
with zipfile.ZipFile('kit.zip','w',zipfile.ZIP_DEFLATED) as z:
    for root,_,fs in os.walk('kx'):
        for f in fs:
            p=os.path.join(root,f); z.write(p,os.path.relpath(p,'kx'))
req=urllib.request.Request(f'https://www.googleapis.com/upload/drive/v3/files/{FID}?uploadType=media&supportsAllDrives=true&fields=id,modifiedTime,size',data=open('kit.zip','rb').read(),method='PATCH',headers={'Authorization':'Bearer '+tok,'Content-Type':'application/zip'})
print('KIT UPLOADED',urllib.request.urlopen(req).read().decode())
