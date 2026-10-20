set -x
pip install -q yt-dlp
mkdir -p tmp_job/out/v
PER=3 python3 tmp_job/commons_fetch.py tmp_job; mv tmp_job/cands tmp_job/out/cands3
for u in \
 "https://agenciagov.ebc.com.br/noticias/202409/pf-em-acao-conjunta-realiza-operacao-para-a-retirada-de-gados-criados-ilegalmente-na-terra-indigena-apyterewa-pa" \
 "https://sbtnews.sbt.com.br/noticia/brasil/operacao-retira-158-bois-e-25-cavalos-criados-ilegalmente-em-terra-indigena-no-para" \
 "https://www.canalrural.com.br/seguranca/mais-de-7-mil-cabecas-de-gado-sao-apreendidas-em-areas-de-desmatamento-ilegal/" \
 "https://www.canalrural.com.br/pecuaria/ibama-apreende-1-730-cabecas-de-gado-em-operacao/" \
 "https://www.canalrural.com.br/seguranca/forca-tarefa-retira-2-mil-cabecas-de-gado-ilegais-no-sudoeste-do-para/" \
 "https://www.cnnbrasil.com.br/politica/assista-ao-video-da-reuniao-ministerial-com-bolsonaro/" \
 "https://www.instagram.com/ibamagov/reels/" ; do
  n=$(echo "$u" | md5sum | cut -c1-6)
  timeout 240 yt-dlp --no-warnings --playlist-items 1-6 -f "bv*[height<=720]+ba/b[height<=720]/b" --merge-output-format mp4 --write-info-json -o "tmp_job/out/v/${n}_%(playlist_index|0)s.%(ext)s" "$u" || echo "FAIL $u"
done
for f in tmp_job/out/v/*.mp4; do ffmpeg -nostdin -v error -y -i "$f" -vf "scale='min(720,iw)':-2" -c:v libx264 -crf 24 -c:a aac -b:a 96k "${f%.mp4}_s.mp4" && mv "${f%.mp4}_s.mp4" "$f"; done
find tmp_job/out/v -size +45M -delete
ls -la tmp_job/out/v
# r3
