import asyncio, os, json, edge_tts
os.makedirs('out/voz',exist_ok=True); log=[]
T="Se você é mãe ou pai, talvez com um filho pequeno, escuta essa história. Ela não questiona o direito de defesa. Não quer vingança. Só quer que a justiça seja feita."
V=[('ava','en-US-AvaMultilingualNeural'),('emma','en-US-EmmaMultilingualNeural'),('vivienne','fr-FR-VivienneMultilingualNeural'),('seraphina','de-DE-SeraphinaMultilingualNeural'),('thalita_calma','pt-BR-ThalitaMultilingualNeural')]
async def go():
    for n,v in V:
        try:
            rate='+5%' 
            c=edge_tts.Communicate(T,v,rate=rate,pitch='-2Hz')
            await c.save(f'out/voz/{n}.mp3'); log.append(f'ok {n} {os.path.getsize(f"out/voz/{n}.mp3")}')
        except Exception as e: log.append(f'fail {n} {e!r}')
asyncio.run(go())
open('out/log.txt','w').write('\n'.join(log)); print('\n'.join(log))
