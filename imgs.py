import requests, json, os, io
from PIL import Image
H={'User-Agent':'reel-research-script/1.0 (github actions)'}
people={'motta':'Hugo Motta','nikolas':'Nikolas Ferreira','marinho':'Rogério Marinho','alcolumbre':'Davi Alcolumbre','tereza':'Tereza Cristina','adriana':'Adriana Ventura','sostenes':'Sóstenes Cavalcante'}
meta={}
def info(fname):
    r=requests.get('https://commons.wikimedia.org/w/api.php',params={'action':'query','titles':'File:'+fname,'prop':'imageinfo','iiprop':'url|extmetadata|size','iiurlwidth':1400,'format':'json'},headers=H).json()
    p=list(r['query']['pages'].values())[0];ii=p['imageinfo'][0];em=ii.get('extmetadata',{})
    g=lambda k:(em.get(k,{}).get('value') or '')[:200]
    return ii.get('thumburl') or ii['url'],{'file':fname,'license':g('LicenseShortName'),'artist':g('Artist'),'w':ii.get('width'),'h':ii.get('height')}
os.makedirs('out/img',exist_ok=True)
for k,t in people.items():
    try:
        r=requests.get('https://pt.wikipedia.org/w/api.php',params={'action':'query','titles':t,'prop':'pageimages','piprop':'name','format':'json','redirects':1},headers=H).json()
        p=list(r['query']['pages'].values())[0];fn=p.get('pageimage')
        url,m=info(fn);b=requests.get(url,headers=H).content
        Image.open(io.BytesIO(b)).convert('RGB').save(f'out/img/{k}.jpg',quality=90);meta[k]=m;print(k,fn,m['license'])
    except Exception as e: print('ERR',k,e)
q={'plen':'Plenário Câmara dos Deputados sessão','plen2':'Plenário da Câmara dos Deputados votação painel','senado':'Plenário do Senado Federal sessão','cong':'Congresso Nacional Brasília cúpulas','gaveta':'arquivo gaveta documentos','microfone':'microfone plenário Câmara dos Deputados'}
for k,s in q.items():
    try:
        r=requests.get('https://commons.wikimedia.org/w/api.php',params={'action':'query','list':'search','srsearch':s+' filetype:bitmap','srnamespace':6,'srlimit':6,'format':'json'},headers=H).json()
        for i,hit in enumerate(r['query']['search'][:4]):
            fn=hit['title'][5:];url,m=info(fn)
            if (m['w'] or 0)<1000: continue
            b=requests.get(url,headers=H).content
            Image.open(io.BytesIO(b)).convert('RGB').save(f'out/img/{k}_{i}.jpg',quality=88);meta[f'{k}_{i}']=m;print(k,i,fn,m['license'])
    except Exception as e: print('ERR',k,e)
json.dump(meta,open('out/img/meta.json','w'),ensure_ascii=False,indent=1)
