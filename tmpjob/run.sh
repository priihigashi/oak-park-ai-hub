set -x
mkdir -p out
yt-dlp -o "out/reel.%(ext)s" --write-info-json "https://www.instagram.com/reel/Dfph3i3Crxf/" || echo FAIL > out/fail.txt
f=$(ls out/reel.mp4 out/reel.* 2>/dev/null | grep -v json | head -1)
[ -n "$f" ] || exit 0
ffmpeg -v error -y -i "$f" -vf "fps=1/2,scale=240:-1,tile=6x6" -frames:v 1 out/sheet.jpg
ffmpeg -v error -y -i "$f" -vf "select='gt(scene,0.3)',scale=240:-1,tile=6x4" -vsync vfr -frames:v 1 out/scenes.jpg
python - <<'P'
from faster_whisper import WhisperModel
import glob,json
f=[x for x in glob.glob('out/reel.*') if not x.endswith('.json')][0]
m=WhisperModel('small',compute_type='int8')
segs,_=m.transcribe(f,language='pt',word_timestamps=True)
out=[];txt=[]
for s in segs:
    out.append({'s':s.start,'e':s.end,'t':s.text,'w':[[w.start,w.end,w.word] for w in s.words]})
    txt.append(f"[{s.start:6.1f}-{s.end:6.1f}] {s.text}")
json.dump(out,open('out/transcript.json','w'),ensure_ascii=False)
open('out/transcript.txt','w').write("\n".join(txt))
P
ls -la out
