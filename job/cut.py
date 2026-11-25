import subprocess
from rembg import remove
from PIL import Image
for name,src,t in [('pav','ig_out/r1.mp4',25.5),('pav2','ig_out/r1.mp4',40),('eri','ig_out/r2.mp4',12),('eri2','ig_out/r2.mp4',47)]:
    subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(t),'-i',src,'-vframes','1',f'job_out/{name}_src.png'])
    im=Image.open(f'job_out/{name}_src.png')
    remove(im).save(f'job_out/{name}_cut.png')
