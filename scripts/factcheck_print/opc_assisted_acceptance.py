"""Exercise downstream OPC media/render/filing with an explicitly assisted draft.

This never marks the failed automatic text run as passed. The replacement draft
is private, hash-bound, source-reviewed in chat, and visibly labeled assisted.
No text API calls; at most the four not-yet-requested images of the original run.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from opc import save, make_assets, finalize_spec, retain_failure
from opc_contract import GateError, validate, digest_file
from opc_media import ReplicateImages
from opc_render import export, review
from opc_store import Store, CAROUSEL_PARENT
from opc_usage import summary


def download_checkpoint(store: Store, file: dict, parent: str, path: Path) -> None:
    meta = store.drive.files().get(fileId=file['id'], fields='parents,size,md5Checksum,mimeType', supportsAllDrives=True).execute()
    if parent not in meta.get('parents', []) or int(meta.get('size', 0)) > 12_000_000:
        raise GateError('Checkpoint ownership or size mismatch')
    if meta.get('mimeType') not in ('application/json', 'image/png'):
        raise GateError('Unexpected checkpoint MIME type')
    data = store.drive.files().get_media(fileId=file['id'], supportsAllDrives=True).execute()
    if not isinstance(data, bytes) or hashlib.md5(data).hexdigest() != meta.get('md5Checksum'):
        raise GateError('Checkpoint checksum mismatch')
    path.write_bytes(data)


def verify_pack(pack: dict, root: Path, run_key: str) -> None:
    if pack.get('mode') != 'assisted_acceptance' or pack.get('original_run_key') != run_key:
        raise GateError('Not the source-bound assisted draft')
    if pack.get('approved') is not False or pack.get('published') is not False:
        raise GateError('Owner approval/publication cannot be supplied by this build')
    review_info = pack.get('editorial_review', {})
    if review_info.get('provider') != 'ChatGPT-assisted' or review_info.get('automated_review_passed') is not False:
        raise GateError('Assisted review cannot be described as an automated pass')
    if pack.get('evidence_sha256') != digest_file(root / 'resources/evidence.json'):
        raise GateError('Source packet changed after assisted review')


def prepare(cli) -> tuple:
    store = Store(); store.preflight()
    folder = store.drive.files().get(fileId=cli.folder_id, fields='id,name,parents,appProperties,webViewLink', supportsAllDrives=True).execute()
    props = folder.get('appProperties', {})
    if CAROUSEL_PARENT not in folder.get('parents', []) or props.get('opcPrintRun') != cli.run_key or props.get('state') != 'BLOCKED_NOT_APPROVED':
        raise GateError('Only the exact blocked OPC run can be completed as an assisted sample')
    sub = [f for f in store.list_children(folder['id']) if f['name'] == 'resources']
    if len(sub) != 1:
        raise GateError('Ambiguous resources folder')
    parent = sub[0]['id']; files = store.list_children(parent)
    if any(f['name'] in ('image-usage.json', 'assisted-build.json') for f in files):
        raise GateError('Images or assisted completion already started; no paid replay')
    root = Path(cli.out); (root / 'resources').mkdir(parents=True, exist_ok=True); (root / 'motion').mkdir(exist_ok=True)
    names = ['evidence.json', 'text-usage.json', 'usage-summary.json', 'topic-plan.json', 'failure.json',
             'assisted-paint-draft.json'] + [f'proof-S{i}.png' for i in range(1, 5)]
    for name in names:
        matches = [f for f in files if f['name'] == name]
        if len(matches) != 1:
            raise GateError('Missing/ambiguous assisted checkpoint: ' + name)
        download_checkpoint(store, matches[0], parent, root / 'resources' / name)
    if digest_file(root / 'resources/assisted-paint-draft.json') != cli.spec_sha256:
        raise GateError('Assisted draft changed before execution')
    pack = json.loads((root / 'resources/assisted-paint-draft.json').read_text())
    verify_pack(pack, root, cli.run_key)
    usage = json.loads((root / 'resources/usage-summary.json').read_text())
    if usage.get('image_requests') != 0:
        raise GateError('Original image budget already used')
    return store, folder, parent, root, pack


def build(store, folder, parent, root, pack) -> dict:
    from run import email
    evidence = json.loads((root / 'resources/evidence.json').read_text())
    if pack['source_urls'] != {s['id']: s['url'] for s in evidence['sources']}:
        raise GateError('Assisted source IDs do not match original research')
    plan = json.loads((root / 'resources/topic-plan.json').read_text())
    if store.duplicates(plan['title'], plan['keywords'], ''):
        raise GateError('Topic was already filed; no duplicate image spend')
    provider = ReplicateImages('google/nano-banana-pro', root)
    marker = root / 'resources/assisted-build.json'
    save(marker, {'mode':'ASSISTED_DOWNSTREAM_ACCEPTANCE','automatic_text_passed':False,
                  'new_text_api_calls':0,'max_image_requests':4,'approved':False,'state':'RESERVED'})
    store.upsert_run_file(marker, parent); store.finish(folder, 'ASSISTED_BUILD_RESERVED')
    a = SimpleNamespace(url='',kind='education',reuse_assets='',static_only=False)
    draft = pack['draft']; editorial = pack['editorial_review']
    assets = make_assets(a, draft, root, store, provider)
    spec = finalize_spec(a, draft, evidence['sources'], assets, editorial, None, plan.get('source_company_aliases', []))
    spec['build_mode'] = 'assisted_downstream_acceptance'
    save(root / 'resources/content-gates.json', validate(spec, root, plan.get('source_company_aliases', [])))
    save(root / 'cards.json', spec); save(root / 'resources/assisted-review.json', editorial)
    store.rename_run(folder, spec['title']); export(spec, root)
    page = review(spec, root)
    page.write_text(page.read_text().replace('READY FOR PRISCILA REVIEW · NOT APPROVED · NOT PUBLISHED',
                   'ASSISTED SAMPLE · NOT AN AUTONOMOUS PASS · NOT APPROVED'), encoding='utf-8')
    (root / 'motion/README.md').write_text('Static idea-mode sample. No video or motion acceptance claimed.\n')
    summary(root)
    links = store.upload_tree(root, folder)
    receipt = {'content_row':store.file_row(spec, folder, links), 'flow_row':store.flow_row(spec, folder, links),
               'build_mode':'assisted_downstream_acceptance','automatic_text_passed':False,'approved':False,'published':False}
    save(root / 'resources/filing-receipt.json', receipt)
    store.upsert_run_file(root / 'resources/filing-receipt.json', parent)
    save(marker, {**receipt,'image_requests':len(provider.records),'state':'ASSISTED_BUILT_NOT_APPROVED'})
    store.upsert_run_file(marker, parent); store.finish(folder, 'ASSISTED_BUILT_NOT_APPROVED')
    email('OPC assisted paint sample — review required',
          'The automatic text run failed and remains recorded as failed. The replacement copy was source-checked in chat.\n'
          'This tests actual image generation, deterministic rendering and verified filing, not autonomous completion.\n'
          f'Review: {folder["webViewLink"]}\nRows: {receipt["content_row"]}; {receipt["flow_row"]}\n'
          'No additional text API calls. Images are illustrations, not OPC job proof or exact paint swatches. Nothing published.',
          [root / 'png/dark/card_01.png'])
    return receipt


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--folder-id',required=True); p.add_argument('--run-key',required=True)
    p.add_argument('--spec-sha256',required=True); p.add_argument('--out',default='opc-assisted-sample')
    cli = p.parse_args(); store,folder,parent,root,pack = prepare(cli)
    try:
        receipt = build(store,folder,parent,root,pack)
        print(json.dumps(receipt))
    except Exception as exc:
        summary(root); retain_failure(exc,store,root,folder)
        print('Assisted downstream build failed: ' + type(exc).__name__)
        raise SystemExit(1) from None

if __name__ == '__main__':main()
