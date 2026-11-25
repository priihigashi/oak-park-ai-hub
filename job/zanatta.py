import requests,os,json
from rembg import remove
from PIL import Image
from io import BytesIO
os.makedirs('job_out',exist_ok=True)
r=requests.get('https://dadosabertos.camara.leg.br/api/v2/deputados',params={'nome':'Julia Zanatta','itens':5},headers={'Accept':'application/json'},timeout=30).json()
json.dump(r,open('job_out/zan_api.json','w'))
d=r['dados'][0]
img=requests.get(d['urlFoto'],timeout=30).content
open('job_out/zan_src.jpg','wb').write(img)
im=Image.open(BytesIO(img)).convert('RGB')
remove(im).save('job_out/zan_cut.png')
