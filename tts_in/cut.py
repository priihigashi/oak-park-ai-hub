import json, os, urllib.request, io
from rembg import remove, new_session
from PIL import Image
P=json.load(open("tts_in/pessoas.json")); os.makedirs("fotos_out",exist_ok=True)
sess=new_session("isnet-general-use")
for slug,url in P.items():
    try:
        raw=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read()
        im=Image.open(io.BytesIO(raw)).convert("RGB")
        im.save(f"fotos_out/{slug}_orig.jpg",quality=90)
        out=remove(im,session=sess)
        bb=out.getbbox(); out=out.crop(bb)
        out.save(f"fotos_out/{slug}.png"); print("ok",slug,out.size)
    except Exception as e: print("ERRO",slug,e)
