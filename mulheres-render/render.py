import sys, pathlib, json, asyncio, base64, subprocess, html, glob, mimetypes, os
import urllib.request
from copy import deepcopy
sys.path.insert(0, 'runner')
import producao as p, cards
out=pathlib.Path('saida'); out.mkdir(exist_ok=True)
scenes=json.loads(pathlib.Path('cenas.json').read_text())['cenas']
# Preserve exact template layout, vary theme and source images per card.
colors=['#D4A64D','#D9C185','#9DB6C8','#D39573','#F2C94C','#A7C6A1','#EAC4A4','#A9C4D6','#C7B9D6','#D9AD75','#E6C86A']
for i,s in enumerate(scenes):
    s['cor_tema']=colors[i%len(colors)]
    if s['card']=='p112': s['campos']['estrela']=False
media_errors=[]
def inline_url(url):
    if not url or not url.startswith('https://'): return url
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=15) as res:
            data=res.read(5_000_000); typ=res.headers.get_content_type()
        if not typ.startswith('image/'): raise ValueError('not image: '+typ)
        return 'data:'+typ+';base64,'+base64.b64encode(data).decode()
    except Exception as e:
        media_errors.append(url+': '+str(e));return ''
for s in scenes:
    for k in ['foto_fundo','midia','foto','foto2']:
        if s['campos'].get(k): s['campos'][k]=inline_url(s['campos'][k])
# Narration: free voice and actual word boundary marks.
fala=' '.join(s['fala'] for s in scenes)
voice=out/'thalita.mp3';words=asyncio.run(p._tts(fala,voice));assert words and voice.stat().st_size>0
m=p.montar_manifesto('NEWS-20261125-MULHERES-2027',1,scenes,words,'voz.mp3')
# Preserve the original segment as the opening; audio is joined to narration.
clip=None;clip_len=0
try:
    src=glob.glob('/tmp/mulheres-original.*')[0]
    clip=out/'trecho-original.mp4'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-ss','78.6','-i',src,'-t','6.0','-vf','scale=540:-2','-c:v','libx264','-preset','fast','-crf','27','-c:a','aac','-movflags','+faststart',str(clip)],check=True)
    clip_len=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(clip)]))
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',str(clip),'-i',str(voice),'-filter_complex','[0:a]aformat=sample_rates=44100:channel_layouts=mono[a0];[1:a]aformat=sample_rates=44100:channel_layouts=mono[a1];[a0][a1]concat=n=2:v=0:a=1[out]','-map','[out]','-c:a','libmp3lame','-q:a','4',str(out/'voz.mp3')],check=True)
    for s in m['scenes']:
        s['start']+=clip_len;s['end']+=clip_len
        def shift(obj):
            if isinstance(obj,dict):
                for k,v in obj.items():
                    if (k=='t' or k.startswith('t_')) and isinstance(v,(int,float)):obj[k]=v+clip_len
                    else:shift(v)
            elif isinstance(obj,list):
                for a in obj:shift(a)
        shift(s.get('campos',{}))
    for w in m['words']:w['start']+=clip_len;w['end']+=clip_len
    m['scenes'].insert(0,{'type':'clip','start':0,'end':clip_len,'title':'Eduarda Campopiano · PL-SP','source':'Congresso em Foco · 25/11/2026','video':'data:video/mp4;base64,'+base64.b64encode(clip.read_bytes()).decode()})
except Exception as e:
    media_errors.append('Original: '+str(e));(out/'voz.mp3').write_bytes(voice.read_bytes())
m['title']='Mulheres mais votadas 2027'
m['pendencias']=(m.get('pendencias') or [])+media_errors+['Divisão ideológica estadual não publicada: conciliar 212/213; vídeos de arquivo adicionais não incluídos.']
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False))
(out/'fala.txt').write_text(fala)
t=pathlib.Path('anim/previa.html').read_text()
status='Prévia com voz gratuita. Fotos oficiais de arquivo. Revisão editorial, clipes oficiais adicionais e auditoria visual final pendentes. '+('; '.join(media_errors) if media_errors else 'Mídia de abertura e fotos processadas.')
replacements={'__TITULO__':m['title'],'__ID__':m['id'],'__V__':'1','__QUANDO__':'25/11/2026','__COR__':'#F2C94C','__SITUACAO__':html.escape(status),'__LEGENDA__':'Rankings de mulheres eleitas e composição das Casas.','__COMENTARIO__':'Fontes: TSE; Agência Câmara; Agência Senado (25/10/2026); HubPolítico; GPS Partidário 2026. Imagens: Agência Câmara e Agência Senado. Original: Congresso em Foco, 25/11/2026.','__MANIFESTO__':json.dumps(m,ensure_ascii=False).replace('</','<\\/')}
for k,v in replacements.items():t=t.replace(k,v)
t=cards.injetar(t)
t=t.replace('src="voz.mp3"','src="data:audio/mpeg;base64,'+base64.b64encode((out/'voz.mp3').read_bytes()).decode()+'"')
needle="if(s.type==='card'&&window.CARDS)"
insert="""if(s.type==='clip'){
let v=P.querySelector('video[data-original]');
if(!v){P.innerHTML='<div style="position:absolute;inset:0;background:#111;display:flex;align-items:center;justify-content:center"><video data-original playsinline muted style="width:100%;height:82%;object-fit:contain"></video><div style="position:absolute;top:130px;left:100px;right:100px;color:#fff;font:bold 44px Rubik,Arial">EDUARDA CAMPOPIANO · PL-SP</div><div style="position:absolute;bottom:150px;left:100px;right:100px;color:#fff;font:30px Rubik,Arial">Congresso em Foco · trecho original</div></div>';v=P.querySelector('video');v.src=s.video}
const ct=t-s.start;if(Math.abs(v.currentTime-ct)>0.28)v.currentTime=ct;v.playbackRate=a.playbackRate;if(a.paused)v.pause();else if(v.paused)v.play().catch(()=>{});return;}
"""
assert needle in t
t=t.replace(needle,insert+needle)
(out/'index.html').write_text(t)
# Independent audio validation and browser render.
try:
    tr=p.transcrever(voice)
    (out/'prova-sync.json').write_text(json.dumps(p.prova_sync(words,tr,fala),ensure_ascii=False))
except Exception as e:(out/'auditoria-pendente.txt').write_text(str(e))
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b=pw.chromium.launch(args=['--no-sandbox']);page=b.new_page(viewport={'width':390,'height':844})
        page.goto((out/'index.html').resolve().as_uri());page.wait_for_timeout(800)
        page.evaluate("document.fonts.ready")
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        for n,s in enumerate(m['scenes']):
            page.evaluate("t=>{document.getElementById('a').currentTime=t;desenhar(t)}",(s['start']+s['end'])/2)
            page.wait_for_timeout(200);page.screenshot(path=str(out/('quadro-%02d.png'%n)))
        page.evaluate("()=>document.getElementById('a').play()");page.wait_for_timeout(600)
        proof={'audioDuration':page.evaluate("document.getElementById('a').duration"),'audioCurrentTime':page.evaluate("document.getElementById('a').currentTime"),'errors':errors,'scenes':len(m['scenes']),'media_errors':media_errors,'original_clip':bool(clip and clip.exists())}
        (out/'prova-player.json').write_text(json.dumps(proof,ensure_ascii=False));b.close()
except Exception as e:(out/'prova-player.json').write_text(json.dumps({'erro':str(e)}))
