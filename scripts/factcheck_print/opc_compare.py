"""Resume the two original engine tests only after zero-generation receipts.

The original pair stopped in capture, before any text/image generation. Their
private failures are preserved. This source-bound transcript fallback does NOT
claim a playable source video or a successful 60-second cut.
"""
from argparse import Namespace
import json
from pathlib import Path
import sys
from opc import prepare, build, file_built, retain_failure, save
from opc_contract import GateError
from opc_usage import summary


def arguments(engine: str) -> Namespace:
    return Namespace(project='opc',url='https://www.youtube.com/watch?v=UsPEjMxywsY',idea='',discover=False,
        engine=engine,image_model='google/nano-banana-pro',notes='Repair the source-linked countertop test. Original English OPC material education, not a rebuttal.',
        notes_file='',out='opc-live-'+engine,rebuild_row=428,static_only=False,
        run_key='pr300-validation-20260920-transcript-resume-'+engine,kind='education',project_group='',reuse_assets='',reuse_capture='')


def build_one(a, previous: str = '') -> dict:
    if previous:
        a.reuse_assets=previous
        prior=json.loads((Path(previous)/'cards.json').read_text())
        if prior.get('video',{}):a.reuse_capture=previous
    store,root,folder=prepare(a)
    try:
        spec=build(a,store,root,folder)
        summary(root)
        return {'ok':True,'a':a,'store':store,'root':root,'folder':folder,'spec':spec}
    except Exception as exc:
        summary(root);retain_failure(exc,store,root,folder)
        return {'ok':False,'a':a,'store':store,'root':root,'folder':folder,
                'failure':{'type':type(exc).__name__,'message':str(exc)[:1000] if isinstance(exc,GateError) else 'Technical failure; inspect private receipts'}}


def main() -> None:
    from opc_capture_cache import verify_zero_generation
    from opc_store import Store
    import os
    store=Store()
    for engine in ('claude','openai'):
        verify_zero_generation(store,'pr300-validation-20260920-'+engine)
    os.environ['OPC_REUSE_FAILED_CAPTURE']='1'
    states=[];previous=''
    for engine in ('claude','openai'):
        try:
            state=build_one(arguments(engine),previous)
            states.append(state)
            if state['ok']:previous=str(state['root'])
        except Exception as exc:
            states.append({'ok':False,'a':arguments(engine),'failure':{'type':type(exc).__name__,'message':'Preflight or persistent run guard blocked this test'}})
    public=[];private=[]
    for state in states:
        engine=state['a'].engine
        if state['ok']:
            try:
                result=file_built(state['a'],state['store'],state['root'],state['folder'],state['spec'])
                private.append({'engine':engine,**result})
            except Exception as exc:
                state['ok']=False;retain_failure(exc,state['store'],state['root'],state['folder'])
                private.append({'engine':engine,'status':'filing_failed','folder':state['folder']})
        else:
            private.append({'engine':engine,'status':'blocked','folder':state.get('folder'),'failure':state['failure']})
        public.append({'engine':engine,'built_and_filed':state['ok'],'approved':False})
    from run import email
    email('OPC PRINT comparison — review required',json.dumps(private,ensure_ascii=False,indent=2))
    print('OPC_COMPARISON '+json.dumps(public))
    if not all(x['built_and_filed'] for x in public):raise SystemExit(1)

if __name__=='__main__':main()
