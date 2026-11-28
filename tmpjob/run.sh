set -x
pip install -q gallery-dl instaloader || true
rm -rf out; mkdir -p out/frames
ID=DgBCgf8NUkI
for u in "https://www.instagram.com/reel/$ID/" "https://www.instagram.com/p/$ID/" "https://www.instagram.com/reels/$ID/"; do
  yt-dlp -o "out/reel.%(ext)s" --write-info-json "$u" >> out/log.txt 2>&1 && break
done
f=$(ls out/reel.* 2>/dev/null | grep -v json | head -1)
if [ -z "$f" ]; then
  gallery-dl -D out/gdl "https://www.instagram.com/p/$ID/" >> out/log.txt 2>&1 || true
  g=$(ls out/gdl/*.mp4 2>/dev/null | head -1); [ -n "$g" ] && mv "$g" out/reel.mp4
fi
if [ -z "$(ls out/reel.mp4 out/reel.webm 2>/dev/null)" ] && [ -z "$f" ]; then
  (cd out && instaloader --no-metadata-json --dirname-pattern=il -- -$ID >> log.txt 2>&1) || true
  g=$(ls out/il/*.mp4 2>/dev/null | head -1); [ -n "$g" ] && mv "$g" out/reel.mp4
  cp out/il/*.txt out/caption_il.txt 2>/dev/null || true
fi
f=$(ls out/reel.* 2>/dev/null | grep -v json | head -1)
[ -n "$f" ] || { echo FAIL > out/fail.txt; tail -60 out/log.txt; exit 0; }
ffmpeg -v error -y -i "$f" -vf "fps=1/2,scale=360:-1" out/frames/f%03d.jpg
python - <<'P'
from faster_whisper import WhisperModel
import glob,json,os
j=glob.glob('out/*.info.json')
if j:
    d=json.load(open(j[0]))
    open('out/meta.txt','w').write(f"uploader: {d.get('uploader')} / {d.get('channel')}\nupload_date: {d.get('upload_date')}\nduration: {d.get('duration')}\nlikes: {d.get('like_count')}\n\nCAPTION:\n{d.get('description')}\n")
    os.remove(j[0])
f=[x for x in glob.glob('out/reel.*') if not x.endswith('.json')][0]
m=WhisperModel('small',compute_type='int8')
segs,info=m.transcribe(f)
open('out/transcript.txt','w').write(f"lang {info.language}\n"+"\n".join(f"[{s.start:6.1f}-{s.end:6.1f}] {s.text}" for s in segs))
P
rm -rf out/reel.* out/gdl out/il
ls -la out
