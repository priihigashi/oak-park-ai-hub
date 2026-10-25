from faster_whisper import WhisperModel
import json,sys
m=WhisperModel('small',compute_type='int8')
segs,_=m.transcribe(sys.argv[1],language='pt',word_timestamps=True)
out=[{'start':s.start,'end':s.end,'text':s.text,'words':[{'w':w.word,'s':w.start,'e':w.end} for w in s.words]} for s in segs]
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False)
