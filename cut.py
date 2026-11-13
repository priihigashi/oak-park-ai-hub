from rembg import remove,new_session
from PIL import Image
import os
s=new_session('u2net_human_seg')
for k in ['motta','nikolas','marinho','alcolumbre','tereza','adriana','sostenes']:
    p=f'out/img/{k}.jpg'
    if not os.path.exists(p): continue
    im=Image.open(p).convert('RGB');im.thumbnail((900,1200))
    o=remove(im,session=s,alpha_matting=True,alpha_matting_foreground_threshold=240,alpha_matting_background_threshold=10,alpha_matting_erode_size=10)
    o.save(f'out/img/{k}_cut.png');print('cut',k)
