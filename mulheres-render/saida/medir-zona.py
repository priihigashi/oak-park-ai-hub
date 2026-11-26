import collections
import hashlib
import json
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parent
manifest_bytes = (root / 'manifest.json').read_bytes()
manifest = json.loads(manifest_bytes)
scenes = manifest['scenes']
reports = []
with sync_playwright() as browser:
    executable = shutil.which('google-chrome') or shutil.which('google-chrome-stable')
    if not executable:
        raise RuntimeError('Chrome indisponível no runner')
    chromium = browser.chromium.launch(executable_path=executable, args=['--no-sandbox'])
    page = chromium.new_page(viewport={'width': 570, 'height': 1250})
    page.goto((root / 'index.html').as_uri(), wait_until='load')
    page.evaluate('() => document.fonts.ready')
    for index, scene in enumerate(scenes):
        times = sorted({(scene['start'] + scene['end']) / 2, *range(int(scene['start']) + 1, int(scene['end']) + 1)})
        for seconds in times:
            problems = page.evaluate("t => { desenhar(t); return CARDS.medir(document.getElementById('palco')).problemas; }", seconds)
            if problems:
                reports.append({'cena': index, 'card': scene.get('card', scene['type']), 't': round(seconds, 2), 'problemas': problems})
    chromium.close()

counts = collections.Counter(item['cena'] for item in reports)
result = {'ok': not reports, 'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(), 'motor': 'player original, CARDS.medir, Chromium', 'fontes': 'fontes do player depois de document.fonts.ready', 'cenas_com_problema': [{'cena': i, 'card': scenes[i].get('card', scenes[i]['type']), 'tempos_com_problemas': n, 'amostra': next(x for x in reports if x['cena'] == i)} for i, n in counts.items()]}
(root / 'auditoria-area-segura.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'ok': result['ok'], 'cenas': counts}, ensure_ascii=False))
