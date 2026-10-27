import os, json, urllib.request, urllib.parse, pathlib, io, subprocess
OUT=pathlib.Path('tmp/tr/out/assets'); OUT.mkdir(parents=True, exist_ok=True)
td=json.loads(os.environ['SHEETS_TOKEN'])
tok=json.loads(urllib.request.urlopen('https://oauth2.googleapis.com/token',urllib.parse.urlencode({'client_id':td['client_id'],'client_secret':td['client_secret'],'refresh_token':td['refresh_token'],'grant_type':'refresh_token'}).encode()).read())['access_token']
def drive(fid,name):
    req=urllib.request.Request(f'https://www.googleapis.com/drive/v3/files/{fid}?alt=media&supportsAllDrives=true',headers={'Authorization':'Bearer '+tok})
    open(OUT/name,'wb').write(urllib.request.urlopen(req).read())
files={'lula2021.png':'1tzgs63axac3xdH4vWA1DTmKUbO5rvaX7','flavio_n.png':'1lDbNaiz7hkNoH1R8oyuVlqhwgAFfS2cs','flavio_agsen.jpg':'1Uyeyn7TpOqUVTPW1AziBvHOid8RQQ1ka','queiroz.jpg':'1qETejWJwdgtJw3MlbILDKXB4BmmDRg88','moro.jpg':'1KBEfuP58dkjcGQsN-geh43EGNP44rbAf','lulinha.svg':'1ITN9Q7xHh-9Q6JrVm3W4YXKxBOiap2pO','lulinha_small.svg':'1vpoVctqLjzInD8IjTZ_9louqasPPsJ1s','lula_oficial.jpg':'1yWtVF3xz9d1q0uH4NU9XQj6OQV2mTJSy'}
log={}
for n,f in files.items():
    try: drive(f,n); log[n]='ok'
    except Exception as e: log[n]=str(e)
UA={'User-Agent':'OakParkBot/1.0 (priscila@oakpark-construction.com)'}
def commons(q,name):
    u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','generator':'search','gsrsearch':q,'gsrnamespace':6,'gsrlimit':5,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':900,'format':'json'})
    d=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA)).read())
    pages=sorted(d.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',99))
    res=[]
    for i,p in enumerate(pages):
        ii=p['imageinfo'][0]; url=ii.get('thumburl') or ii['url']
        fn=f'{name}_{i}.jpg'
        try:
            open(OUT/fn,'wb').write(urllib.request.urlopen(urllib.request.Request(url,headers=UA)).read())
            md=ii.get('extmetadata',{})
            res.append({'file':fn,'title':p['title'],'author':md.get('Artist',{}).get('value','')[:200],'license':md.get('LicenseShortName',{}).get('value','')})
        except Exception as e: res.append({'err':str(e)})
    return res
for q,n in [('Léo Pinheiro OAS','pinheiro'),('Fabrício Queiroz','queirozc'),('Sergio Moro 2019','moroc'),('Flávio Bolsonaro senador','flavioc'),('Michelle Bolsonaro 2019','michelle')]:
    try: log[n]=commons(q,n)
    except Exception as e: log[n]=str(e)
json.dump(log,open(OUT/'log.json','w'),ensure_ascii=False,indent=1)
