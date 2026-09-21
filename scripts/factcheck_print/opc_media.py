"""Real source capture and explicit-model Replicate illustrations for OPC."""
from __future__ import annotations

import base64
import contextlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

import requests
from PIL import Image, ImageOps

from opc_contract import GateError, MODELS, MAX_IMAGES, digest_file
from opc_network import download

STYLE = ('A photograph, not a render. Realistic documentary photography, honest material texture and small imperfections. '
         'Lighting must physically match the requested scene. If the subject explicitly requests a controlled comparison, keep camera/room/material constant and change only the requested lighting or finish variable across panels. '
         'No text, letters, numbers, labels, signage or logos. Avoid identifiable people; a hand/tool may appear only when needed to demonstrate a real process. ')
WORLD = ('A consistent contemporary South Florida home aesthetic: current, well-kept furnishings, warm neutral surfaces and light oak accents. '
         'Avoid visibly worn or dated staging unless the subject requires it. Use the actual room, material, objects, camera geometry and lighting requested in the subject, not an unrelated kitchen. '
         'Quiet uncluttered composition. Match photographic treatment only, not previous content. ')


def probe(path: Path) -> dict:
    p = subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],
                       check=True, capture_output=True, text=True, timeout=30)
    raw = json.loads(p.stdout)
    return {'duration': float(raw['format']['duration']),
            'has_video': any(s.get('codec_type') == 'video' for s in raw['streams']),
            'has_audio': any(s.get('codec_type') == 'audio' for s in raw['streams'])}


def sanitize_photo(source: Path, target: Path) -> None:
    with Image.open(source) as opened:
        im = ImageOps.exif_transpose(opened).convert('RGB')
        im.thumbnail((1440, 1440))
        clean = Image.new('RGB', im.size)
        clean.paste(im)
        clean.save(target, 'JPEG', quality=90)
    with Image.open(target) as check:
        if check.getexif() or min(check.size) < 300:
            raise GateError('Image metadata/dimensions failed validation')


def _pytube_video(url: str, tmp: str) -> str:
    from pytubefix import YouTube
    stream = YouTube(url).streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    return stream.download(output_path=tmp, filename='source-fallback.mp4') if stream else ''


def _download_source(url: str, tmp: str) -> tuple[str, list[dict]]:
    import capture_pipeline as cp
    routes = [('existing_cookie_ios_routes', cp.download_video), ('pytubefix_progressive', _pytube_video),
              ('existing_apify_media_route', cp._try_apify_youtube_download)]
    attempts = []
    for name, route in routes:
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                source = route(url, tmp)
            media = probe(Path(source)) if source else {}
            if media.get('has_video') and media.get('has_audio'):
                attempts.append({'route': name, 'status': 'success'})
                return source, attempts
            attempts.append({'route': name, 'status': 'no_playable_video'})
        except Exception as exc:
            attempts.append({'route': name, 'status': 'failed', 'error_type': type(exc).__name__})
    raise GateError('Source video could not be retrieved by the existing cookie/iOS, progressive or media routes; no placeholder is marked ready')


def capture(url: str, root: Path) -> dict:
    """No calls to capture_pipeline.main/process: no stray briefs/folders/rows."""
    from faster_whisper import WhisperModel
    with tempfile.TemporaryDirectory() as tmp:
        source, attempts = _download_source(url, tmp)
        meta = probe(Path(source))
        if meta['duration'] > 1800 or Path(source).stat().st_size > 250_000_000:
            raise GateError('Source exceeds 30-minute / 250 MB bounded capture limit')
        full = root / 'resources/source-full.mp4'
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',source,'-vf','scale=720:-2','-c:v','libx264',
                        '-crf','27','-preset','fast','-c:a','aac','-b:a','96k','-movflags','+faststart',str(full)],
                       check=True, capture_output=True, timeout=300)
    iterator, info = WhisperModel('base', device='cpu', compute_type='int8').transcribe(str(full), vad_filter=True)
    segments = [{'start': round(s.start,2), 'end': round(s.end,2), 'text': s.text.strip()} for s in iterator]
    if not segments or sum(len(s['text']) for s in segments) < 60:
        raise GateError('No usable transcript; refusing an invented video summary')
    result = {'source_url': url, 'full_file': 'resources/source-full.mp4', 'duration_in': meta['duration'],
              'language_detected': info.language, 'segments': segments, 'routes': attempts, 'full_sha256':digest_file(full),
              'transcript': ' '.join(s['text'] for s in segments)}
    (root/'resources/capture.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


def cut_video(captured: dict, indices: list[int], root: Path) -> dict:
    from fit_video import render
    full = root / captured['full_file']
    target = root / 'resources/source-preview.mp4'
    duration = probe(full)['duration']
    speed = 1.0
    if duration <= 60:
        shutil.copyfile(full, target)
        picks = [[0, duration]]
    else:
        segs = captured['segments']
        if not indices or indices != sorted(set(indices)) or any(not isinstance(i,int) or i < 0 or i >= len(segs) for i in indices):
            raise GateError('Video cut must use ordered whole transcript segments')
        picks = [[segs[i]['start'],segs[i]['end']] for i in indices]
        total = sum(b-a for a,b in picks)
        if any(b <= a for a,b in picks) or total > 70.5:
            raise GateError('Selected whole segments exceed the comfortable 60-second budget')
        speed = 1.2
        render(full, target, picks, speed)
    result = probe(target)
    if result['duration'] > 60 or not result['has_video'] or not result['has_audio']:
        raise GateError('Rendered preview failed ffprobe duration/audio/video gate')
    return {'file': str(target.relative_to(root)), 'duration_in': duration, 'duration_out': result['duration'],
            'speed': speed, 'kept': picks, 'sha256': digest_file(target), 'placement': 'private_review_only'}


class ReplicateImages:
    MAX_REQUESTS = MAX_IMAGES * 3
    def __init__(self, model: str, root: Path, max_images: int = MAX_IMAGES):
        if model not in MODELS or not 1 <= max_images <= self.MAX_REQUESTS:
            raise GateError('Unsupported image model or image request budget')
        key = os.getenv('PRI_OP_REPLICATE_API_KEY')
        if not key:
            raise GateError('Existing PRI_OP_REPLICATE_API_KEY is unavailable')
        self.model, self.root, self.max_images = model, root, max_images
        self.headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
        usage=root/'resources/image-usage.json'
        try:self.records=json.loads(usage.read_text(encoding='utf-8')) if usage.exists() else []
        except Exception:self.records=[]
        self.schema = self._request('GET',f'/models/{model}')['latest_version']['openapi_schema']['components']['schemas']['Input']

    def switch_model(self, model: str) -> None:
        if model not in MODELS:
            raise GateError('Unsupported fallback image model')
        self.model=model
        self.schema=self._request('GET',f'/models/{model}')['latest_version']['openapi_schema']['components']['schemas']['Input']

    def _request(self, method: str, path: str, **kw) -> dict:
        if not re.fullmatch(r'/(?:models/[\w.-]+/[\w.-]+(?:/predictions)?|predictions/[\w-]+)', path):
            raise GateError('Invalid Replicate API path')
        r = requests.request(method, 'https://api.replicate.com/v1'+path, headers=self.headers, timeout=90, **kw)
        if not r.ok:
            raise GateError(f'Replicate request failed HTTP {r.status_code}; response body withheld from public logs')
        return r.json()

    def _input(self, subject: str, anchor: Path | None) -> dict:
        props = self.schema.get('properties', {})
        values = {'prompt': STYLE+WORLD+subject, 'aspect_ratio':'16:9','output_format':'png',
                  'resolution':'2K','size':'2K','max_images':1,'sequential_image_generation':'disabled',
                  'allow_fallback_model':False}
        if anchor and 'image_input' in props:
            values['image_input'] = ['data:image/jpeg;base64,'+base64.b64encode(anchor.read_bytes()).decode()]
        result = {k:v for k,v in values.items() if k in props}
        if 'prompt' not in result or any(k not in result for k in self.schema.get('required',[])):
            raise GateError('Replicate schema changed; required input is missing')
        return result

    def _save(self) -> None:
        (self.root/'resources/image-usage.json').write_text(json.dumps(self.records,indent=2),encoding='utf-8')

    def generate(self, key: str, subject: str, anchor: Path | None = None) -> dict:
        if not re.fullmatch(r'A[1-5]',key) or len(self.records) >= self.max_images:
            raise GateError('Image limit reached or invalid asset key')
        record = {'key':key,'model':self.model,'status':'request_started','estimated_usd':None,
                  'cost_note':'Provider invoice not returned by prediction API; count recorded, amount unknown'}
        self.records.append(record);self._save()
        prediction = self._request('POST',f'/models/{self.model}/predictions',json={'input':self._input(subject,anchor)})
        record['prediction_id'] = prediction['id'];self._save()
        for _ in range(90):
            if prediction['status'] in ('succeeded','failed','canceled'):
                break
            time.sleep(3)
            prediction = self._request('GET',f"/predictions/{prediction['id']}")
        record.update(status=prediction['status'], metrics=prediction.get('metrics',{}));self._save()
        if prediction['status'] != 'succeeded':
            raise GateError('Replicate image did not complete; no silent provider/model fallback')
        outputs = prediction.get('output')
        url = outputs[0] if isinstance(outputs,list) and outputs else outputs
        if not isinstance(url,str):
            raise GateError('Replicate returned no image URL')
        raw = self.root / f'resources/{key}-raw'
        target = self.root / f'resources/{key}.jpg'
        download(url,raw);sanitize_photo(raw,target);raw.unlink()
        return {'key':key,'path':str(target.relative_to(self.root)),'sha256':digest_file(target),
                'kind':'ai_illustration','model':self.model,'prediction_id':prediction['id'],
                'subject':subject, 'prompt':STYLE+WORLD+subject, 'style_anchor':str(anchor.relative_to(self.root)) if anchor else None}
