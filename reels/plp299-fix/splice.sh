set -e
cd reels/plp299-fix
cat orig/o.mp4.part_* > /tmp/orig.mp4
E="-c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 44100 -ac 1"
fadeA(){ echo "afade=t=in:st=0:d=0.04,afade=t=out:st=$(python3 -c "print(max(0,$1-0.04))"):d=0.04"; }
seg(){ # orig segment by frames
  s=$1; e=$2; out=$3; d=$(python3 -c "print(($e-$s)/30)")
  ffmpeg -y -loglevel error -i /tmp/orig.mp4 -filter_complex "[0:v]trim=start_frame=$s:end_frame=$e,setpts=PTS-STARTPTS[v];[0:a]atrim=start=$(python3 -c "print($s/30)"):end=$(python3 -c "print($e/30)"),asetpts=PTS-STARTPTS,$(fadeA $d)[a]" -map "[v]" -map "[a]" $E $out
}
newseg(){ # scene frames dir + voice file a0 a1
  dir=$1; mp3=$2; a0=$3; a1=$4; out=$5
  n=$(ls $dir/f*.jpg | wc -l); d=$(python3 -c "print($n/30)")
  ffmpeg -y -loglevel error -framerate 30 -i $dir/f%05d.jpg -i site/a/$mp3 -filter_complex "[1:a]atrim=start=$a0:end=$a1,asetpts=PTS-STARTPTS,atempo=1.15,apad,atrim=end=$d,$(fadeA $d)[a]" -map 0:v -map "[a]" $E -t $d $out
}
mkdir -p /tmp/segs
seg 0 4608 /tmp/segs/01.mp4
newseg frames/c07 nv1.mp3 0 36.08 /tmp/segs/02.mp4
seg 5134 5491 /tmp/segs/03.mp4
newseg frames/c09 nv2.mp3 0 11.66 /tmp/segs/04.mp4
seg 5778 6450 /tmp/segs/05.mp4
newseg frames/c12 nv3.mp3 0 27.49 /tmp/segs/06.mp4
newseg frames/c13 nv4.mp3 0 31.07 /tmp/segs/07.mp4
newseg frames/c14 nv5.mp3 0 51.45 /tmp/segs/08.mp4
N=$(ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -of csv=p=0 /tmp/orig.mp4)
seg 7883 $N /tmp/segs/09.mp4
for f in /tmp/segs/*.mp4; do echo "file '$f'"; done > /tmp/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i /tmp/list.txt -c copy -movflags +faststart /tmp/final.mp4
for f in /tmp/segs/*.mp4; do echo "$f $(ffprobe -v error -show_entries format=duration -of csv=p=0 $f)"; done
ffprobe -v error -show_entries format=duration -of csv=p=0 /tmp/final.mp4
