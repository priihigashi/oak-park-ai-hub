set -x
rm -rf out; mkdir -p out
pip install -q edge-tts
python tmpjob/tts.py
ls -la out
