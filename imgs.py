import requests, json, os, io, traceback
from PIL import Image
H={'User-Agent':'ReelResearchBot/1.0 (https://github.com/priihigashi)','Accept':'application/json'}
os.makedirs('out/img',exist_ok=True)
log=open('out/img/log.txt','w')
meta={}
def save(k,url,m):
    b=requests.get(url,headers={'User-Agent':H['User-Agent']},timeout=60).content
    im=Image.open(io.BytesIO(b)).convert('RGB');im.save(f'out/img/{k}.jpg',quality=92);m['size']=im.size;meta[k]=m;print(k,m,file=log,flush=True)
dep={'motta':'Hugo Motta','nikolas':'Nikolas Ferreira','adriana':'Adriana Ventura','sostenes':'Sóstenes Cavalcante','gilberto':'Cabo Gilberto'}
for k,n in dep.items():
    try:
        r=requests.get('https://dadosabertos.camara.leg.br/api/v2/deputados',params={'nome':n},headers=H,timeout=60).json()['dados']
        d=r[0];save(k,d['urlFoto'],{'src':'Câmara dos Deputados (foto oficial)','nome':d['nome'],'partido':d['siglaPartido'],'uf':d['siglaUf']})
    except Exception: print('ERR',k,traceback.format_exc(),file=log,flush=True)
try:
    L=requests.get('https://legis.senado.leg.br/dadosabertos/senador/lista/atual.json',headers=H,timeout=60).json()
    P=L['ListaParlamentarEmExercicio']['Parlamentares']['Parlamentar']
    for k,n in {'marinho':'Rogerio Marinho','alcolumbre':'Davi Alcolumbre','tereza':'Tereza Cristina'}.items():
        for p in P:
            i=p['IdentificacaoParlamentar']
            nm=i['NomeParlamentar'].replace('é','e')
            if n.lower() in nm.lower():
                save(k,i['UrlFotoParlamentar'],{'src':'Senado Federal (foto oficial)','nome':i['NomeParlamentar'],'partido':i.get('SiglaPartidoParlamentar')});break
        else: print('NOTFOUND',k,file=log)
except Exception: print('ERR senado',traceback.format_exc(),file=log,flush=True)
def info(fname):
    r=requests.get('https://commons.wikimedia.org/w/api.php',params={'action':'query','titles':'File:'+fname,'prop':'imageinfo','iiprop':'url|extmetadata|size','iiurlwidth':1600,'format':'json'},headers=H,timeout=60).json()
    p=list(r['query']['pages'].values())[0];ii=p['imageinfo'][0];em=ii.get('extmetadata',{})
    g=lambda k:(em.get(k,{}).get('value') or '')[:200]
    return ii.get('thumburl') or ii['url'],{'file':fname,'license':g('LicenseShortName'),'artist':g('Artist'),'w':ii.get('width'),'h':ii.get('height')}
q={'plen':'Plenário Câmara dos Deputados','senado':'Plenário Senado Federal Brasil','cong':'Congresso Nacional Brasília','painel':'painel votação Câmara dos Deputados','eleicao':'eleição presidente Câmara dos Deputados'}
for k,s in q.items():
    try:
        r=requests.get('https://commons.wikimedia.org/w/api.php',params={'action':'query','list':'search','srsearch':s,'srnamespace':6,'srlimit':10,'format':'json'},headers=H,timeout=60).json()
        n=0
        for hit in r['query']['search']:
            fn=hit['title'][5:]
            if not fn.lower().endswith(('.jpg','.jpeg','.png')): continue
            url,m=info(fn)
            if (m['w'] or 0)<1200: continue
            save(f'{k}_{n}',url,m);n+=1
            if n>=3: break
    except Exception: print('ERR',k,traceback.format_exc(),file=log,flush=True)
json.dump(meta,open('out/img/meta.json','w'),ensure_ascii=False,indent=1)
