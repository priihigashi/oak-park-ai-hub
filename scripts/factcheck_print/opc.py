"""OPC PRINT orchestration. Build + evidence + review, never schedule/publish."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'capture'))
sys.path.insert(0,str(HERE.parent))

from opc_contract import AI_DISCLOSURE, GateError, MODELS, STATUS, check_copy, digest_file, named_competitor, plain, validate, safe_relative
from opc_llm import Model
from opc_media import ReplicateImages, sanitize_photo
from opc_capture_cache import capture, cut_video
from opc_network import screenshot_candidates
from opc_render import export, review
from opc_store import Store, CONTROL, CONTROL_TAB
from resolve_inputs import video_url


def save(path: Path, value) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')


def options() -> argparse.Namespace:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',default='opc',choices=['opc'])
    ap.add_argument('--url',default='')
    ap.add_argument('--idea',default='')
    ap.add_argument('--discover',action='store_true')
    ap.add_argument('--engine',choices=['auto','claude','openai'],default=os.getenv('FC_ENGINE','auto'))
    ap.add_argument('--image-model',choices=MODELS,default=MODELS[0])
    ap.add_argument('--notes',default='');ap.add_argument('--notes-file',default='')
    ap.add_argument('--out',default='factcheck_out')
    ap.add_argument('--rebuild-row',type=int,default=0)
    ap.add_argument('--static-only',action='store_true')
    ap.add_argument('--run-key',default='')
    ap.add_argument('--kind',choices=['education','project_proof'],default='education')
    ap.add_argument('--project-group',default='')
    ap.add_argument('--reuse-assets',default='')
    ap.add_argument('--reuse-capture',default='')
    a=ap.parse_args()
    if os.getenv('FC_INPUT_FILE'):
        data=json.loads(Path(os.environ['FC_INPUT_FILE']).read_text())
        for key in ('url','idea','engine','image_model','rebuild_row','static_only','notes'):
            if key in data:setattr(a,key,data[key])
        a.discover=data.get('mode')=='discover'
    if a.notes_file:a.notes=Path(a.notes_file).read_text(encoding='utf-8')[:4000]
    if a.url and not video_url(a.url):raise GateError('Unsupported source video URL')
    if not (a.url or a.idea or a.discover):raise GateError('A video, topic or find-idea request is required')
    if a.kind=='project_proof' and not a.project_group:raise GateError('Project proof requires an exact verified project group')
    return a


def identify(model: Model, a, captured: dict, store: Store) -> dict:
    context={'request':a.idea or a.url,'notes':a.notes,'kind':a.kind,
             'transcript_segments':captured.get('segments',[])}
    if a.discover:
        context['existing_opc_ideas']=store.ideas()
    prompt='''Identify the useful OPC homeowner topic. Return {"title":"3-5 English words about the topic only",
"keywords":["exactly","three","topic-keywords"],"source_company_aliases":["all third-party contractor/channel names in the transcript"],
"keep_segment_indices":[0,1],"candidates":[{"title":"...","why":"...","visual_plan":"...","source":"actual supplied source"}],
"selected_idea":"..."}. For find-idea mode provide three OPC candidates from the supplied ideas and select one.
No competitor names in the title or selected idea. For a source longer than 60 seconds select chronological
whole segments carrying the hook/material distinctions, total duration <=70 seconds. Indices are zero-based.
Do not copy the source company's quote or marketing claims into the final content.'''
    return model.ask(prompt,context)


def research(model: Model, plan: dict) -> dict:
    return model.ask('''Search the web in English for primary evidence for this OPC topic. Return
{"facts":[{"id":"F1","finding":"one useful, qualified material/care fact","explanation":"scope and limits",
"sources":[{"name":"source organization","url":"EXACT URL observed in search","title":"headline"}]}]}.
Return 3-4 facts. For each, seek up to three interchangeable real primary sources that support that SAME fact.
Use official care guides or technical associations, not competing contractors. Avoid unsupported prices and
national averages masquerading as local quotes. Do not invent any URL. A video is inspiration, not evidence.''',plan,web=True)


def gather_evidence(model: Model, findings: dict, root: Path) -> tuple[list, list]:
    facts=findings.get('facts',[])
    if not 3<=len(facts)<=4:raise GateError('Research must yield 3-4 supported teaching points')
    sources=[];evidence=[]
    for i,fact in enumerate(facts,1):
        source,attempts=screenshot_candidates(fact.get('sources',[]),model.search_urls,root,f'S{i}')
        sources.append(source)
        evidence.append({'id':f'F{i}','source_id':f'S{i}','finding':plain(fact.get('finding')),
                         'explanation':plain(fact.get('explanation')),'screenshot_attempts':attempts,
                         'actual_source_excerpt':source.get('excerpt','')})
    save(root/'resources/evidence.json',{'facts':evidence,'sources':sources,'retrieved_at':datetime.now(timezone.utc).isoformat()})
    return sources,evidence


FEED_PROMPT='''Create an Instagram-friendly ORIGINAL OPC carousel, not a fact-check debate. English only.
Return {"title":"short English topic","caption":"150-200 characters before disclosure and sources",
"hashtags":"3-5 relevant hashtags", "slides":[{"id":1,"layout":"cover|point|compare|close",
"headline":"3-7 words, max 70 characters", "body":"max 150 characters; headline+body <=35 words",
"source_ids":["S1"],"visual_key":"A1","visual_description":"what the image shows"}],
"visuals":[{"key":"A1","subject":"photograph scene, no text or labels"}]}.
Create 5-8 cards: hook, 3-5 sequential useful points, one save/decision close. Every middle card has a
supporting source_id supplied in the evidence. No quotes, raw markup, competitor names, debunk badges,
promises, generic filler, invented prices, or claims about completed OPC work. Explain trade words briefly.
Make exactly 4 visually DISTINCT material close-ups or practical scenes, but in the same photographic style.
Every card references one of those visuals. Never ask the image model to write text, draw charts or invent
before/after results. Use a trivet or material sample, not a damaging test presented as a real experiment.
Sources will appear outside the core copy. The caption must not describe illustrations as OPC's own project.'''


def write_feed(model: Model, plan: dict, evidence: list, a) -> dict:
    data={'topic':plan['title'],'evidence':evidence,'kind':a.kind,'notes':a.notes}
    if a.kind=='project_proof':
        data['verified_photo_notes']=getattr(a,'photo_notes',[])
        data['photo_rule']='Use only these exact A1-A4 photos and phases. No invented transformations, project address, customer identity or results.'
    if a.reuse_assets:
        data['available_visuals']=[{'key':x['key'],'subject':x.get('subject','')} for x in json.loads((Path(a.reuse_assets)/'cards.json').read_text())['assets']]
        data['media_rule']='Reuse these exact keys and scenes; do not assign a different meaning to an existing image.'
    raw=model.ask(FEED_PROMPT,data)
    copy_errors=[e for i,c in enumerate(raw.get('slides',[]),1) for e in check_copy(c,i)]
    if copy_errors:
        raw=model.ask(FEED_PROMPT+' Repair these length/schema failures without adding facts.',{'draft':raw,'errors':copy_errors,'evidence':evidence})
    return raw


def approve_editorial(model: Model, draft: dict, evidence: list, aliases: list) -> dict:
    result=model.ask('''Review this draft against the ACTUAL source excerpts, independently of its drafting prompt.
Check every factual claim, English language, contractor voice, coherent sequence, unsupported specificity,
misleading images, excessive text, and the ban on competitor names. Do not approve claims the excerpts do
not support. Return {"passed":true|false,"issues":["..."],"english":true|false}. This is a second request
on the same provider, not a human or independent Council approval. Do not rewrite source evidence.''',
                    {'draft':draft,'evidence':evidence,'banned_names':aliases})
    if result.get('passed') is not True or result.get('english') is not True or result.get('issues'):
        raise GateError('Editorial/source review failed; no ready status was written')
    return {'passed':True,'english':True,'provider':model.engine,'model':model.model,'independent_council':False,
            'method':'separate prompt/request; final owner approval still required'}


def reuse_assets(previous: Path, visuals: list, root: Path) -> list:
    data=json.loads((previous/'cards.json').read_text(encoding='utf-8'))
    assets=data['assets']
    if len(assets)!=len(visuals):raise GateError('Comparison reuse requires the same asset count')
    for asset in assets:
        path=safe_relative(previous,asset['path'])
        if digest_file(path)!=asset['sha256']:raise GateError('Reuse asset hash changed')
        shutil.copyfile(path,root/asset['path'])
    return assets


def make_assets(a, draft: dict, root: Path, store: Store, provider) -> list[dict]:
    visuals=draft.get('visuals',[])
    if not 3<=len(visuals)<=4 or [x.get('key') for x in visuals]!=[f'A{i}' for i in range(1,len(visuals)+1)]:
        raise GateError('Expected 3-4 sequential unique visual plans')
    if a.reuse_assets:return reuse_assets(Path(a.reuse_assets),visuals,root)
    if a.kind=='project_proof':
        rows=store.photos(a.project_group)
        if len(rows)<len(visuals):raise GateError('Not enough approved real project photos; AI is forbidden as project proof')
        assets=[]
        for visual,row in zip(visuals,rows):
            raw=root/f'resources/{visual["key"]}-raw';target=root/f'resources/{visual["key"]}.jpg'
            store.download_photo(row,raw);sanitize_photo(raw,target);raw.unlink()
            assets.append({'key':visual['key'],'kind':'opc_photo','path':str(target.relative_to(root)),
                           'sha256':digest_file(target),'identity_verified':True,'tracker_id':row['Stable ID'],'phase':row['Phase']})
        return assets
    assets=[]
    for visual in visuals:
        anchor=root/assets[0]['path'] if assets else None
        assets.append(provider.generate(visual['key'],plain(visual['subject']),anchor))
    return assets


def finalize_spec(a, raw: dict, sources: list, assets: list, editorial: dict, video: dict | None, aliases: list) -> dict:
    slides=[]
    for i,card in enumerate(raw['slides'],1):
        slides.append({'id':i,'layout':card.get('layout','point'),'headline':plain(card.get('headline')),
                       'body':plain(card.get('body')),'source_ids':card.get('source_ids',[]),
                       'visual_key':card.get('visual_key'),'visual_description':plain(card.get('visual_description'))})
    caption=plain(raw.get('caption'))
    if any(x['kind']=='ai_illustration' for x in assets):caption+=' '+AI_DISCLOSURE
    caption+=' Sources: '+', '.join(dict.fromkeys(s['name'] for s in sources))+'.'
    spec={'project':'opc','language':'en','kind':a.kind,'status':STATUS,'approved':False,'title':plain(raw.get('title')),
          'caption':caption,'hashtags':plain(raw.get('hashtags')),'slides':slides,
          'sources':[{k:s[k] for k in ('id','name','url','screenshot','observed_in_search','heading') if k in s} for s in sources],'assets':assets,
          'editorial_review':editorial,'video':video,'source_url':a.url,'template':'opc_tip / FORMAT-030 visual PRINT',
          'reference_media_status':'playable_file' if video else 'source_link_only' if a.url else 'not_applicable',
          'motion':{'requested':not a.static_only,'status':'static_fallback','reason':'No owned motion clip supplied; Ken Burns and fabricated job footage are not used.'}}
    if named_competitor(json.dumps(spec,ensure_ascii=False),aliases):raise GateError('Competitor in output data')
    return spec


def notify(spec: dict, folder: dict, receipt: dict, root: Path) -> None:
    from run import email
    reference_note=('Source video file: available in private review.' if spec.get('video') else
                    'SOURCE VIDEO FILE UNAVAILABLE: no playable file or 60-second cut is claimed.' if spec.get('source_url') else
                    'Idea-based post: source video and transcription do not apply.')
    body=(f'OPC visual carousel is built, NOT APPROVED.\n\nReview and resources: {folder["webViewLink"]}\n'
          f'Cards: {len(spec["slides"])}. Three visual variants use the same assets.\n'
          f'Tracker readback: {receipt["content_row"]}\nFlow Plans readback: {receipt["flow_row"]}\n'
          f'{reference_note}\n'
          'Motion: static fallback because no owned clip was supplied.\n'
          'Automated editorial pass used a separate request on the same provider; not an independent Council approval.\n'
          'Nothing was scheduled, published or approved. Usage and technical checks are in resources/.')
    email('OPC review: '+spec['title'],body,[root/'png/dark/card_01.png'])


def captured_input(a, root: Path) -> dict:
    if not a.url:return {}
    if not a.reuse_capture:return capture(a.url,root)
    previous=Path(a.reuse_capture)
    data=json.loads((previous/'resources/capture.json').read_text())
    if data['source_url']!=a.url or digest_file(safe_relative(previous,data['full_file']))!=data.get('full_sha256'):
        raise GateError('Comparison capture did not match the original source/digest')
    shutil.copyfile(safe_relative(previous,data['full_file']),root/'resources/source-full.mp4')
    save(root/'resources/capture.json',data)
    return data


def prepare(a) -> tuple[Store,Path,dict]:
    root=Path(a.out);(root/'resources').mkdir(parents=True,exist_ok=True);(root/'motion').mkdir(exist_ok=True)
    store=Store();store.preflight()
    if a.url:
        hits=store.duplicates('Source check',['source','video','link'],a.url,a.rebuild_row)
        if hits:raise GateError('Existing OPC source found in tracker rows '+','.join(map(str,hits)))
    key=a.run_key or os.getenv('GITHUB_RUN_ID') or str(uuid.uuid4())
    folder=store.start_run('OPC visual review',key)
    save(root/'resources/run.json',{'run_key':key,'commit':os.getenv('GITHUB_SHA'),'status':'started','approved':False})
    return store,root,folder


def build(a, store: Store, root: Path, folder: dict) -> dict:
    model=Model(a.engine,root/'resources/text-usage.json');model.preflight()
    provider=None if a.kind=='project_proof' or a.reuse_assets else ReplicateImages(a.image_model,root)
    if a.kind=='project_proof':
        rows=store.photos(a.project_group)
        if len(rows)<4:raise GateError('Four verified photos from the same project are required')
        a.photo_notes=[{'key':f'A{i}', 'phase':x['Phase'], 'description':x['Alt-text Draft']} for i,x in enumerate(rows[:4],1)]
    captured=captured_input(a,root)
    plan=identify(model,a,captured,store)
    save(root/'resources/topic-plan.json',plan)
    aliases=[plain(x) for x in plan.get('source_company_aliases',[])]
    if store.duplicates(plan['title'],plan['keywords'],a.url,a.rebuild_row):raise GateError('Topic already exists; rebuild must be explicitly linked')
    video=cut_video(captured,plan.get('keep_segment_indices',[]),root) if captured else None
    findings=research(model,plan)
    save(root/'resources/research-results.json',findings)
    sources,evidence=gather_evidence(model,findings,root)
    draft=write_feed(model,plan,evidence,a)
    save(root/'resources/feed-draft.json',draft)
    from opc_editorial import review_or_repair
    draft,editorial=review_or_repair(model,draft,evidence,aliases,root/'resources')
    save(root/'resources/feed-draft.json',draft)
    save(root/'resources/editorial-review.json',editorial)
    assets=make_assets(a,draft,root,store,provider)
    spec=finalize_spec(a,draft,sources,assets,editorial,video,aliases)
    gate=validate(spec,root,aliases);save(root/'cards.json',spec);save(root/'resources/content-gates.json',gate)
    store.rename_run(folder,spec['title'])
    export(spec,root);review(spec,root)
    (root/'motion/README.md').write_text(spec['motion']['reason']+'\n',encoding='utf-8')
    return spec


def file_built(a, store: Store, root: Path, folder: dict, spec: dict) -> dict:
    links=store.upload_tree(root,folder)
    receipt={'content_row':store.file_row(spec,folder,links),'flow_row':store.flow_row(spec,folder,links),'approved':False,'published':False}
    save(root/'resources/filing-receipt.json',receipt)
    resources=next(f for f in store.list_children(folder['id']) if f['name']=='resources')
    store.upsert_run_file(root/'resources/filing-receipt.json',resources['id'])
    notify(spec,folder,receipt,root);store.finish(folder,'BUILT_NOT_APPROVED')
    return {'status':'built_not_approved','folder':folder,'receipt':receipt,'cards':len(spec['slides']),'engine':spec['editorial_review']['provider']}


def retain_failure(exc: Exception, store: Store, root: Path, folder: dict) -> None:
    message=str(exc)[:1000] if isinstance(exc,GateError) else 'See provider error type; raw request/secret details are withheld.'
    save(root/'resources/failure.json',{'status':'BLOCKED_NOT_APPROVED','error_type':type(exc).__name__,'message':message})
    try:
        store.upload_tree(root,folder);store.finish(folder,'BLOCKED_NOT_APPROVED')
    except Exception:
        pass


def run(a) -> dict:
    store,root,folder=prepare(a)
    try:
        spec=build(a,store,root,folder)
        from opc_usage import summary
        summary(root)
        return file_built(a,store,root,folder,spec)
    except Exception as exc:
        from opc_usage import summary
        summary(root)
        retain_failure(exc,store,root,folder)
        raise


def main() -> None:
    try:
        result=run(options())
        print(json.dumps({k:v for k,v in result.items() if k!='folder'}))
    except Exception as exc:
        print(f'OPC BLOCKED ({type(exc).__name__}). No approval/publication; inspect the private run receipt.')
        raise SystemExit(1) from None

if __name__=='__main__':main()
