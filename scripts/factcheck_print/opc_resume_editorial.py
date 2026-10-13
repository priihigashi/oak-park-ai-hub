"""Resume only an existing source-reviewed OPC idea run before any image billing.

The exact run folder, measured usage and failed review are verified first.
Concurrency is serialized by the invoking workflow. A durable recovery marker
prevents a second paid repair, even after a runner crash. No new run key/folder.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from types import SimpleNamespace

from opc import save, make_assets, finalize_spec, file_built, retain_failure
from opc_contract import GateError, validate
from opc_editorial import repair_after_review
from opc_llm import Model
from opc_media import ReplicateImages
from opc_render import export, review
from opc_store import Store, CAROUSEL_PARENT
from opc_usage import summary

ALLOWED = re.compile(r'(?:[a-z][a-z0-9-]*\.json|proof-S[1-4]\.png)\Z')


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def fetch_resources(store: Store, folder: dict, root: Path) -> str:
    children = store.list_children(folder['id'])
    if any(x['name'] in ('cards.json', 'review.html', 'png') for x in children):
        raise GateError('Existing rendered output requires a different non-billed resume path')
    resources = [x for x in children if x['name'] == 'resources']
    if len(resources) != 1:
        raise GateError('Expected one run-owned resources folder')
    seen = set()
    for file in store.list_children(resources[0]['id']):
        name = file['name']
        if name in ('image-usage.json', 'editorial-resume.json'):
            raise GateError('Media billing or editorial recovery already started; not replayed')
        if not ALLOWED.fullmatch(name) or name in seen:
            raise GateError('Unexpected or duplicate checkpoint filename')
        seen.add(name)
        meta = store.drive.files().get(fileId=file['id'], fields='size,md5Checksum,mimeType', supportsAllDrives=True).execute()
        if int(meta.get('size', 0)) > 12_000_000 or meta['mimeType'] not in ('application/json', 'image/png'):
            raise GateError('Checkpoint file type/size outside bounds')
        data = store.drive.files().get_media(fileId=file['id'], supportsAllDrives=True).execute()
        if not isinstance(data, bytes) or hashlib.md5(data).hexdigest() != meta.get('md5Checksum'):
            raise GateError('Checkpoint download checksum mismatch')
        (root / 'resources' / name).write_bytes(data)
    return resources[0]['id']


def verify_checkpoint(root: Path, run_key: str) -> tuple[dict, dict, int]:
    resources = root / 'resources'
    saved_run = read_json(resources / 'run.json')
    failure = read_json(resources / 'failure.json')
    usage = read_json(resources / 'text-usage.json')
    counts = read_json(resources / 'usage-summary.json')
    if saved_run.get('run_key') != run_key or counts.get('image_requests') != 0:
        raise GateError('Wrong run or previous media request; refusing paid replay')
    if failure.get('message') != 'Editorial/source review failed; no ready status was written':
        raise GateError('Only the exact pre-media editorial failure can resume here')
    entries = usage.get('entries', [])
    if not entries or any(e.get('engine') != 'claude' or e.get('status') != 'measured_response' for e in entries):
        raise GateError('Usage is missing or uncertain; cannot resume within a verified budget')
    results = sorted(resources.glob('model-result-*.json'))
    calls = len(results)
    if not 1 <= calls <= 5 or [p.name for p in results] != [f'model-result-{i:02d}.json' for i in range(1, calls + 1)]:
        raise GateError('Cannot establish remaining text-call budget')
    failed = read_json(results[-1])
    if failed.get('passed') is not False or not failed.get('issues'):
        raise GateError('Missing original failed editorial verdict')
    return usage, failed, calls


def recover(a, store: Store, folder: dict, root: Path, resources_id: str) -> dict:
    usage, failed, calls = verify_checkpoint(root, a.run_key)
    evidence = read_json(root / 'resources/evidence.json')
    plan = read_json(root / 'resources/topic-plan.json')
    if store.duplicates(plan['title'], plan['keywords'], ''):
        raise GateError('Topic was filed since the failed attempt; no duplicate work')
    model = Model('claude', root / 'resources/text-usage.json')
    model.preflight()
    model.entries = usage['entries']; model.calls = calls
    model.search_urls = {s['url'] for s in evidence['sources'] if s.get('observed_in_search')}
    provider = ReplicateImages('google/nano-banana-pro', root)
    marker = root / 'resources/editorial-resume.json'
    save(marker, {'original_run_key': a.run_key, 'original_calls': calls, 'max_total_calls': 7,
                  'max_image_requests': 4, 'commit': os.getenv('GITHUB_SHA'), 'status': 'REPAIR_RESERVED'})
    store.upsert_run_file(marker, resources_id)
    store.finish(folder, 'EDITORIAL_REPAIR_RESERVED')
    shutil.copyfile(root / 'resources/failure.json', root / 'resources/failure-initial.json')
    aliases = plan.get('source_company_aliases', [])
    draft, editorial = repair_after_review(model, read_json(root / 'resources/feed-draft.json'),
                                            evidence['facts'], aliases, root / 'resources', failed)
    save(root / 'resources/editorial-review.json', editorial)
    assets = make_assets(a, draft, root, store, provider)
    spec = finalize_spec(a, draft, evidence['sources'], assets, editorial, None, aliases)
    save(root / 'resources/content-gates.json', validate(spec, root, aliases))
    save(root / 'cards.json', spec)
    store.rename_run(folder, spec['title'])
    export(spec, root); review(spec, root)
    (root / 'motion/README.md').write_text(spec['motion']['reason'] + '\n')
    summary(root)
    result = file_built(a, store, root, folder, spec)
    save(marker, {'original_run_key': a.run_key, 'status': 'REPAIRED_BUILT_NOT_APPROVED',
                  'total_calls': model.calls, 'image_requests': len(provider.records)})
    store.upsert_run_file(marker, resources_id)
    save(root / 'resources/failure.json', {'status': 'RECOVERED_NOT_APPROVED', 'original_failure': 'failure-initial.json'})
    store.upsert_run_file(root / 'resources/failure.json', resources_id)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder-id', required=True)
    parser.add_argument('--run-key', required=True)
    parser.add_argument('--out', default='opc-paint-resumed')
    cli = parser.parse_args()
    store = Store(); store.preflight()
    folder = store.drive.files().get(fileId=cli.folder_id, fields='id,name,parents,appProperties,webViewLink', supportsAllDrives=True).execute()
    props = folder.get('appProperties', {})
    if CAROUSEL_PARENT not in folder.get('parents', []) or props.get('opcPrintRun') != cli.run_key or props.get('state') != 'BLOCKED_NOT_APPROVED':
        raise GateError('Not the exact blocked OPC run-owned folder')
    root = Path(cli.out); (root / 'resources').mkdir(parents=True, exist_ok=True); (root / 'motion').mkdir(exist_ok=True)
    resources_id = fetch_resources(store, folder, root)
    a = SimpleNamespace(**vars(cli), url='', kind='education', reuse_assets='', static_only=False)
    try:
        result = recover(a, store, folder, root, resources_id)
        print(json.dumps({'status': result['status'], 'cards': result['cards'], 'approved': False}))
    except Exception as exc:
        summary(root); retain_failure(exc, store, root, folder)
        print('OPC editorial recovery blocked: ' + type(exc).__name__)
        raise SystemExit(1) from None

if __name__ == '__main__':
    main()
