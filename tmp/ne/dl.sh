set -x
D=tmp/ne; mkdir -p $D/out/vid
while read k u; do
  timeout 300 yt-dlp --impersonate chrome -f "bv*[height<=1280]+ba/b" --merge-output-format mp4 --max-downloads 4 --match-filter "duration<400" --no-playlist -o "$D/out/vid/${k}_%(autonumber)s.%(ext)s" --write-info-json "$u" || timeout 300 yt-dlp -f "b" -o "$D/out/vid/${k}_%(autonumber)s.%(ext)s" --write-info-json "$u" || echo "FAIL $k" >> $D/out/vid/fails.txt
done < $D/urls.txt
ls -la $D/out/vid
