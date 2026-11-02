import os, re, traceback, requests, io
os.makedirs('out', exist_ok=True)
log=open('out/log.txt','w')
UA={'User-Agent':'Mozilla/5.0'}
base='https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/precos-revenda-e-de-distribuicao-combustiveis/shlp/'
names=['mensal/mensal-brasil-desde-jan2013.xlsx','mensal/mensal-estados-desde-jan2013.xlsx','mensal/mensal-regioes-desde-jan2013.xlsx','semanal/semanal-brasil-desde-2013.xlsx','semanal/semanal-estados-desde-2013.xlsx']
for n in names:
    try:
        r=requests.get(base+n,headers=UA,timeout=120); print(n,r.status_code,len(r.content),file=log)
        if r.ok and len(r.content)>10000: open('out/'+n.split('/')[-1],'wb').write(r.content)
    except Exception as e: print(n,'ERR',e,file=log)
try:
    pg=requests.get('https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/precos-revenda-e-de-distribuicao-combustiveis/serie-historica-do-levantamento-de-precos',headers=UA,timeout=60).text
    links=sorted(set(re.findall(r'href="([^"]+\.xlsx)"',pg)))
    print('\n'.join(links),file=log)
except Exception as e: print('page',e,file=log)
log.close()
