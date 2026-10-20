set -x
pip install -q yt-dlp edge-tts
mkdir -p tmp_job/out
python3 tmp_job/commons_fetch.py tmp_job PER=3 || true
PER=3 python3 tmp_job/commons_fetch.py tmp_job
mv tmp_job/cands tmp_job/out/cands
