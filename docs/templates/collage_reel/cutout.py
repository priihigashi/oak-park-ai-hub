import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as nd
def cut(src, box, out, tol):
    im = np.asarray(Image.open(src).convert('RGB').crop(box)).astype(int)
    h,w,_ = im.shape
    corners = np.array([im[3,3], im[3,w-4], im[h-4,3], im[h-4,w-4]])
    bg = np.median(corners,axis=0)
    d = np.sqrt(((im-bg)**2).sum(-1))
    bgl = d < tol
    lab,_ = nd.label(bgl)
    border = set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]]))) - {0}
    bgmask = np.isin(lab, list(border))
    fg = ~bgmask
    fg = nd.binary_opening(fg, iterations=2)
    lab2,n = nd.label(fg); 
    if n>1:
        sizes = nd.sum(fg, lab2, range(1,n+1)); fg = lab2 == (1+np.argmax(sizes))
    fg = nd.binary_fill_holes(fg); fg = nd.binary_erosion(fg, iterations=4)
    ys,xs = np.where(fg); 
    a = (fg*255).astype(np.uint8)
    rgba = np.dstack([im.astype(np.uint8), a])
    img = Image.fromarray(rgba).crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
    img = img.resize((img.width*2, img.height*2), Image.LANCZOS)
    al = img.split()[3].filter(ImageFilter.GaussianBlur(1.2)); img.putalpha(al)
    img.save(out); print(out, img.size, bg)
import sys
if __name__=='__main__': cut(sys.argv[1], tuple(map(int,sys.argv[2].split(','))), sys.argv[3], int(sys.argv[4]) if len(sys.argv)>4 else 60)
