import requests,io,json
from PIL import Image
H={'User-Agent':'ReelResearchBot/1.0 (https://github.com/priihigashi)'}
log=open('out/img/adri_log.txt','w')
r=requests.get('https://dadosabertos.camara.leg.br/api/v2/deputados',params={'nome':'Adriana Ventura'},headers={**H,'Accept':'application/json'}).json()
print(r,file=log)
for d in r.get('dados',[]):
    for u in [d['urlFoto'],d['urlFoto'].replace('http://','https://'),f"https://www.camara.leg.br/internet/deputado/bandep/{d['id']}.jpg",f"https://www.camara.leg.br/internet/deputado/bandep/pagina_do_deputado/{d['id']}.jpg"]:
        b=requests.get(u,headers=H).content
        print(u,len(b),b[:20],file=log)
        try:
            im=Image.open(io.BytesIO(b)).convert('RGB');im.save('out/img/adriana.jpg',quality=92);print('OK',u,im.size,file=log);break
        except Exception as e: pass
    break
try:
    from rembg import remove,new_session
    im=Image.open('out/img/adriana.jpg');o=remove(im,session=new_session('u2net_human_seg'));o.save('out/img/adriana_cut.png')
except Exception as e: print('cut err',e,file=log)
