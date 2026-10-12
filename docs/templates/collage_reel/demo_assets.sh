#!/usr/bin/env bash
# Gera assets/demo/* usados por repertorio.html (fotos de domínio público do scikit-image: astronauta NASA + cameraman).
set -e; cd "$(dirname "$0")"; mkdir -p assets/demo
python3 -c "import skimage" 2>/dev/null || pip install -q scikit-image --break-system-packages
python3 - <<'PY'
from skimage import data; from PIL import Image, ImageDraw, ImageFilter
im=Image.fromarray(data.astronaut()).convert('RGBA').crop((110,0,370,330)).resize((780,990),Image.LANCZOS)
m=Image.new('L',im.size,0); ImageDraw.Draw(m).ellipse((90,40,690,1100),fill=255); im.putalpha(m.filter(ImageFilter.GaussianBlur(40)))
im.save('assets/demo/_face.png'); Image.fromarray(data.camera()).convert('RGBA').resize((1024,1024)).save('assets/demo/_cam.png')
PY
for e in 1f30d 1f4da 1f441 1f99c; do node svg2png.js assets/$e.svg assets/$e.png 1200; done
python3 linescreen.py assets/demo/_face.png assets/demo/face_red.png --ink "#E3241B" --period 8
python3 linescreen.py assets/demo/_face.png assets/demo/face_blue.png --ink "#2D33E8" --period 8
python3 -c "from PIL import Image,ImageOps; ImageOps.mirror(Image.open('assets/demo/face_blue.png')).save('assets/demo/face_blue.png')"
python3 linescreen.py assets/demo/_face.png assets/demo/face_yellow.png --ink "#F4D21F" --bg "#123d1c" --period 9 --angle 35
python3 linescreen.py assets/demo/_cam.png assets/demo/cam_lines.png --ink "#F2F2F2" --bg "#0d0d0d" --period 6
python3 linescreen.py assets/1f30d.png assets/demo/globe_lines.png --ink "#EEEEEE" --period 7 --gamma .8
python3 linescreen.py assets/1f4da.png assets/demo/books_lines.png --ink "#DDDDDD" --period 6
python3 linescreen.py assets/1f441.png assets/demo/eye_lines.png --ink "#EEEEEE" --period 6
echo "OK assets/demo"
