set -x
pip install -q "rembg[cpu]" transformers torch --extra-index-url https://download.pytorch.org/whl/cpu
mkdir -p tmp_job/out
python3 tmp_job/proc.py
PER=3 python3 tmp_job/commons_fetch.py tmp_job
rm -rf tmp_job/out/cands2; mv tmp_job/cands tmp_job/out/cands2
# r2
