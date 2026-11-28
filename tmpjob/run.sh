set -x
mkdir -p out/frames
yt-dlp -o "out/reel.%(ext)s" --write-info-json "https://www.instagram.com/reel/DgBCgf8NUkI/" || echo FAIL > out/fail.txt
f=$(ls out/reel.* 2>/dev/null | grep -v json | head -1)
[ -n "$f" ] || exit 0
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
rm -f out/reel.*
ls -la out
