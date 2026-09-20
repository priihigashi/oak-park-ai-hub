"""GitHub event inputs are data, never interpolated shell programs."""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
from urllib.parse import urlparse

ALLOWED_HOSTS={'instagram.com','www.instagram.com','m.instagram.com','tiktok.com','www.tiktok.com','vm.tiktok.com','m.tiktok.com','youtube.com','www.youtube.com','m.youtube.com','youtu.be'}
IMAGE_MODELS={'google/nano-banana-pro','google/imagen-4','bytedance/seedream-4.5'}


def video_url(value: str) -> bool:
    try:
        p=urlparse(value)
        return p.scheme=='https' and p.hostname in ALLOWED_HOSTS and not p.username and not p.password and p.port in (None,443) and bool(p.path) and not any(c.isspace() for c in value)
    except ValueError:
        return False


def issue_input(env: dict) -> dict:
    if env.get('ISSUE_AUTHOR')!='priihigashi':
        raise ValueError('Only the owner may start a paid issue-triggered run')
    title=env.get('ISSUE_TITLE','')
    if not title.startswith(('opc-print:','factcheck:')):
        raise ValueError('Unrecognized trigger prefix')
    project='opc' if title.startswith('opc-print:') else 'brazil'
    payload=title.split(':',1)[1].strip()
    url=payload if project!='opc' or video_url(payload) else ''
    idea='' if url else payload
    discover=idea.lower() in ('find an idea','find idea','procure uma ideia')
    return {'url':url,'idea':'' if discover else idea,'notes':env.get('ISSUE_BODY','') or '',
            'project':project,'engine':'auto','discover':discover}


def validate_input(data: dict) -> None:
    if data['project'] not in ('brazil','usa','opc') or data['engine'] not in ('auto','claude','openai'):
        raise ValueError('Invalid project or engine')
    if data['url'] and not video_url(data['url']):
        raise ValueError('Use a single-line HTTPS video-platform URL')
    if data['project']!='opc' and not data['url']:
        raise ValueError('News requires a video URL')
    if not data['url'] and not data['idea'] and not data['discover']:
        raise ValueError('Supply a video link, an idea, or the find-idea option')


def resolve(env: dict) -> dict:
    data={'url':env.get('IN_URL','').strip(),'idea':env.get('IN_IDEA','').strip(),
          'notes':env.get('IN_NOTES',''),'project':env.get('IN_PROJECT') or 'brazil',
          'engine':env.get('IN_ENGINE') or 'auto','discover':env.get('IN_DISCOVER','').lower()=='true'}
    if env.get('EVT')=='issues':data=issue_input(env)
    validate_input(data)
    model=env.get('IN_IMAGE_MODEL') or 'google/nano-banana-pro'
    if model not in IMAGE_MODELS:raise ValueError('Unsupported image model')
    rebuild=env.get('IN_REBUILD_ROW') or '0'
    if not re.fullmatch(r'\d{1,5}',rebuild):raise ValueError('Invalid rebuild row')
    return {**data,'idea':data['idea'][:1000],'notes':data['notes'][:4000],
            'mode':'link' if data['url'] else 'idea' if data['idea'] else 'discover',
            'image_model':model,'rebuild_row':int(rebuild),'static_only':env.get('IN_STATIC_ONLY','').lower()=='true'}


def main() -> None:
    data=resolve(dict(os.environ))
    Path('fc_inputs.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    Path('fc_notes.txt').write_text(data['notes'],encoding='utf-8')
    with open(os.environ['GITHUB_ENV'],'a',encoding='utf-8') as f:
        for key,value in {'FC_URL':data['url'],'FC_PROJECT':data['project'],'FC_ENGINE':data['engine'],
                          'FC_NOTES_FILE':'fc_notes.txt','FC_INPUT_FILE':'fc_inputs.json'}.items():
            if '\n' in str(value) or '\r' in str(value):raise ValueError('Multiline environment value blocked')
            f.write(f'{key}={value}\n')

if __name__=='__main__':main()
