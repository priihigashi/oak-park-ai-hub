import json, os, base64, time, requests
job=json.load(open('job.json'))
el=job.get('el') or {}
if not el: raise SystemExit(0)
K=os.environ.get('ELEVENLABS_API_KEY','')
H={'xi-api-key':K}
os.makedirs('out/tts_el',exist_ok=True)
def sub():
    r=requests.get('https://api.elevenlabs.io/v1/user/subscription',headers=H,timeout=60)
    return {'status':r.status_code,'body':(r.json() if r.ok else r.text[:500])}
info={'before':sub()}
if el.get('balance_only'):
    json.dump(info,open('out/tts_el/balance.json','w'),indent=1); raise SystemExit(0)
vid=el['voice_id']; model=el.get('model','eleven_multilingual_v2')
log={}
for k,t in el['lines'].items():
    if os.path.exists(f'out/tts_el/{k}.mp3') and not el.get('force'): log[k]='exists'; continue
    for attempt in range(3):
        r=requests.post(f'https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128',headers=H,
            json={'text':t,'model_id':model,'voice_settings':el.get('settings',{'stability':0.5,'similarity_boost':0.75,'style':0.0,'use_speaker_boost':True})},timeout=300)
        if r.ok:
            d=r.json(); open(f'out/tts_el/{k}.mp3','wb').write(base64.b64decode(d['audio_base64']))
            json.dump(d.get('alignment'),open(f'out/tts_el/{k}.align.json','w'),ensure_ascii=False)
            log[k]='ok'; break
        log[k]=f'err {r.status_code} {r.text[:300]}'
        if r.status_code<500 and r.status_code!=429: break
        time.sleep(15)
info['log']=log; info['after']=sub()
json.dump(info,open('out/tts_el/log.json','w'),indent=1,ensure_ascii=False)
