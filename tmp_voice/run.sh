set -x
pip install -q edge-tts yt-dlp
mkdir -p tmp_voice/out/v
VOICE=pt-BR-AntonioNeural python3 tmp_voice/tts_edge.py tmp_voice
mv tmp_voice/tts tmp_voice/out/tts; mv tmp_voice/words.json tmp_voice/out/
for u in https://www.youtube.com/watch?v=nnZdP2cvwvw https://www.youtube.com/watch?v=-Fk2-WvnS2E https://www.youtube.com/watch?v=uhLUEQ-zBzM; do
  id=${u##*=}
  yt-dlp --no-warnings -f "bv*[height<=720]+ba/b[height<=720]" --merge-output-format mp4 -o "tmp_voice/out/v/$id.%(ext)s" "$u" || echo "FAIL $u"
done
ls -la tmp_voice/out/v
