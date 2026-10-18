"""Recorte colorido + fundo P&B ("pessoa colorida, mundo cinza").
uso: python3 colorpop.py entrada.mp4 saida.mp4 cx [fps] [start] [dur] [zoom] [cy]
 - cx/cy: centro da pessoa (0..1) no quadro original; o recorte vertical 9:16 centraliza ali
 - zoom: 1 = altura inteira; 1.3 = aproxima 30%
Segmentação: MediaPipe selfie_segmenter (rápido, ~30 ms/quadro em CPU) + suavização temporal.
Fundo: P&B, escurecido, contraste alto. Pessoa: cor original, saturação +18%. Halo branco sutil.
Variável SEG_MODEL aponta para o .tflite (selfie_segmenter.tflite).
"""
import sys, subprocess, os
import numpy as np, cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

MODEL = os.environ.get('SEG_MODEL', '/tmp/claude-0/models/tmp_models/seg.tflite')
src, dst, cx = sys.argv[1], sys.argv[2], float(sys.argv[3])
fps = float(sys.argv[4]) if len(sys.argv) > 4 else 24
start = float(sys.argv[5]) if len(sys.argv) > 5 else 0
dur = float(sys.argv[6]) if len(sys.argv) > 6 else 8
zoom = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
cy = float(sys.argv[8]) if len(sys.argv) > 8 else 0.5
W, H = 720, 1280

cap = cv2.VideoCapture(src)
sfps = cap.get(cv2.CAP_PROP_FPS) or 30
iw, ih = int(cap.get(3)), int(cap.get(4))
ch = ih / zoom; cw = ch * 9 / 16
if cw > iw: cw = iw; ch = cw * 16 / 9
x0 = int(max(0, min(iw - cw, iw * cx - cw / 2))); y0 = int(max(0, min(ih - ch, ih * cy - ch / 2)))
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=BaseOptions(model_asset_path=MODEL), output_confidence_masks=True))
ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                       '-c:v', 'libx264', '-crf', '22', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', dst], stdin=subprocess.PIPE)
n = int(dur * fps); prev = None; k = np.ones((9, 9), np.uint8)
for i in range(n):
    cap.set(cv2.CAP_PROP_POS_MSEC, (start + i / fps) * 1000)
    ok, fr = cap.read()
    if not ok: break
    fr = cv2.resize(fr[y0:y0 + int(ch), x0:x0 + int(cw)], (W, H), interpolation=cv2.INTER_LANCZOS4)
    rgb = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
    a = np.squeeze(seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)).confidence_masks[0].numpy_view()).astype(np.float32)
    a = np.clip((a - 0.3) / 0.45, 0, 1)
    if prev is not None: a = 0.6 * a + 0.4 * prev
    prev = a
    a = cv2.GaussianBlur(a, (0, 0), 1.2)[..., None]
    g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    g = np.clip((g - 128) * 1.25 + 128, 0, 255) * 0.58
    gray = np.repeat(g[..., None], 3, 2)
    hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV).astype(np.float32); hsv[..., 1] = np.clip(hsv[..., 1] * 1.18, 0, 255)
    col = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
    glow = cv2.GaussianBlur(cv2.dilate(a[..., 0], k), (0, 0), 7)[..., None] * 0.28
    base = gray * (1 - glow) + 255 * glow
    out = col * a + base * (1 - a)
    ff.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait()
print(dst, n, 'frames', f'crop x0={x0} y0={y0} {int(cw)}x{int(ch)} from {iw}x{ih}')
