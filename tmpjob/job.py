import requests,os
os.makedirs('out/voz',exist_ok=True)
r=requests.get("https://api.us.elevenlabs.io/v1/voices/fpqzllOdDmER4wwFESLO/previews/audio?payload=eyJ2b2ljZV9zb3VyY2UiOiJjdXN0b20iLCJ3b3Jrc3BhY2VfaWQiOiJjMzQ5MTRjZDZiYTI0NzhmODZkZjE4ZWI1MDZkOTU2MSIsImZpbGVuYW1lIjoiNzE0MTAwYTgtYzY1Ny00NTA0LWI2ZTgtZDgwOWU4MmVjY2YwLm1wMyIsInRpbWVzdGFtcCI6MTc5MjcwNjQwMDAwMDAwMH0%3D",timeout=60,headers={'User-Agent':'Mozilla/5.0'})
open('out/voz/athena_preview.mp3','wb').write(r.content)
open('out/log.txt','w').write(f'athena {r.status_code} {len(r.content)} {r.headers.get("content-type")}')
