import os, sys, glob, numpy as np
from PIL import Image
from rembg import remove, new_session
from transformers import pipeline
src='tmp_job/in'; out='tmp_job/out/proc'; os.makedirs(out,exist_ok=True)
s=new_session('isnet-general-use')
for f in glob.glob(src+'/h_*.jpg'):
    im=Image.open(f).convert('RGB'); r=remove(im,session=s); r.save(f"{out}/{os.path.basename(f)[:-4]}.png")
dp=pipeline('depth-estimation',model='depth-anything/Depth-Anything-V2-Small-hf')
for f in glob.glob(src+'/p_*.jpg'):
    im=Image.open(f).convert('RGB'); d=dp(im)['depth']; d.save(f"{out}/{os.path.basename(f)[:-4]}_depth.png")
