pip install -q yt-dlp
mkdir -p res
yt-dlp --skip-download --dump-json 'https://www.instagram.com/reel/DdU3ADIuEba/' > res/meta.json 2> res/meta_err.txt || true
python -c "
import json
try:
  d=json.load(open('res/meta.json'))
  open('res/meta.txt','w').write('\n'.join(f'{k}: {d.get(k)}' for k in ['uploader','uploader_id','channel','title','description','timestamp','upload_date','like_count','comment_count']))
except Exception as e: open('res/meta.txt','w').write('ERR '+str(e))
"
