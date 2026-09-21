"""Read a source-bound existing capture; never treat an AI brief as transcript."""
import json
import re
from pathlib import Path
from opc_contract import GateError, canonical_url, digest_file
from routing import capture_folder


def read_text(store, file: dict, maximum: int = 100_000) -> str:
    meta=store.drive.files().get(fileId=file['id'],fields='size,mimeType',supportsAllDrives=True).execute()
    if meta.get('mimeType') not in ('text/plain','application/json') or int(meta.get('size',0))>maximum:
        raise GateError('Stored capture has an unexpected MIME type or size')
    raw=store.drive.files().get_media(fileId=file['id'],supportsAllDrives=True).execute()
    return raw.decode('utf-8') if isinstance(raw,bytes) else str(raw)


def cached_capture(url: str, root: Path, store) -> dict:
    target=canonical_url(url)
    children=store.list_children(capture_folder('opc'))
    for folder in reversed(children):
        if folder.get('mimeType')!='application/vnd.google-apps.folder':continue
        vid=target.split('v=')[-1] if 'youtube.com/watch?v=' in target else ''
        if not vid or vid not in folder.get('name',''):continue
        candidates=[f for f in store.list_children(folder['id']) if f['name']=='transcript.txt']
        if len(candidates)!=1:continue
        text=read_text(store,candidates[0])
        match=re.search(r'^SOURCE:\s*(https://\S+)',text,re.M)
        if not match or canonical_url(match[1])!=target:continue
        if len(text)<200 or re.search(r'\[(?:TRANSCRIPT_UNAVAILABLE|MEDIA RETRIEVAL BLOCKED)\]',text):continue
        path=root/'resources/source-transcript.txt';path.write_text(text,encoding='utf-8')
        result={'source_url':url,'transcript':text,'segments':[{'text':text}],
                'transcript_file':str(path.relative_to(root)),'transcript_sha256':digest_file(path),
                'transcript_origin':'existing source-bound Drive capture','source_capture_id':folder['id'],
                'video_available':False,'full_file':None,
                'reference_warning':'Source video download is unavailable. This feed is based on the saved transcript and newly checked sources; no playable source file or 60-second cut is claimed.'}
        (root/'resources/capture.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print('OPC_REFERENCE_WARNING: no source video file; using a source-bound saved transcript. Private review must show this warning.')
        return result
    raise GateError('No source-bound saved transcript. Source capture requires a retrievable video or its original transcript; no fabricated placeholder is accepted')


def verify_zero_generation(store, key: str) -> None:
    matches=[f for f in store.list_children(__import__('opc_store').CAROUSEL_PARENT) if f.get('appProperties',{}).get('opcPrintRun')==key]
    if len(matches)!=1 or matches[0].get('appProperties',{}).get('state')!='BLOCKED_NOT_APPROVED':
        raise GateError('Resume is limited to the exact blocked validation')
    resources=[f for f in store.list_children(matches[0]['id']) if f['name']=='resources']
    if len(resources)!=1:raise GateError('Missing prior private usage receipt')
    files=store.list_children(resources[0]['id'])
    usage=next((f for f in files if f['name']=='usage-summary.json'),None)
    failure=next((f for f in files if f['name']=='failure.json'),None)
    if not usage or not failure:raise GateError('Cannot establish a generation-free capture failure')
    counts=json.loads(read_text(store,usage));reason=json.loads(read_text(store,failure))
    if counts.get('text_responses')!=0 or counts.get('image_requests')!=0 or 'Source video could not be retrieved' not in reason.get('message',''):
        raise GateError('Prior generation already occurred; an automatic paid restart is prohibited')


def capture(url: str, root: Path) -> dict:
    import os
    import opc_media
    from opc_store import Store
    if os.getenv('OPC_REUSE_FAILED_CAPTURE') == '1':
        return cached_capture(url,root,Store())
    try:
        return opc_media.capture(url,root)
    except GateError as exc:
        if not str(exc).startswith('Source video could not be retrieved'):
            raise
        return cached_capture(url,root,Store())


def cut_video(captured: dict, indices: list[int], root: Path):
    import opc_media
    if captured.get('video_available') is False:
        return None
    return opc_media.cut_video(captured,indices,root)
