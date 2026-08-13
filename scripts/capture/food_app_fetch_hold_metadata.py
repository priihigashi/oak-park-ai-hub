#!/usr/bin/env python3
"""Fetch captions/transcripts for the 12 Food App recipes still on source HOLD."""
from __future__ import annotations
import json, os, pathlib, requests

KEY=os.getenv('APIFY_API_KEY','').strip()
ACTOR='https://api.apify.com/v2/acts/apify~instagram-reel-scraper/run-sync-get-dataset-items'
OUT=pathlib.Path('food-app-hold-metadata'); OUT.mkdir(parents=True,exist_ok=True)
SOURCES={
 449:'https://www.instagram.com/reel/DbLp24KMT-p/',
 452:'https://www.instagram.com/reel/DY0PfAQh2DG/',
 453:'https://www.instagram.com/reel/DYfrfp6uAOC/',
 454:'https://www.instagram.com/reel/Da-3RpARvrZ/',
 456:'https://www.instagram.com/reel/DalgAUXRqXv/',
 457:'https://www.instagram.com/reel/DYrzGWPRoTK/',
 465:'https://www.instagram.com/reel/DbT2V_Tyn_b/',
 467:'https://www.instagram.com/reel/DX9An9juZ4n/',
 468:'https://www.instagram.com/reel/DQwmws6ACOn/',
 472:'https://www.instagram.com/reel/DaLxj7Wx2s-/',
 514:'https://www.instagram.com/reel/DZvea4HPr-q/',
 526:'https://www.instagram.com/reel/Db4GFW7SJZR/',
}

def code(url): return url.rstrip('/').split('/')[-1]
def main():
    if not KEY: raise RuntimeError('APIFY_API_KEY missing')
    response=requests.post(ACTOR,params={'token':KEY},json={
        'username':list(SOURCES.values()),
        'resultsLimit':1,
        'includeTranscript':True,
        'includeDownloadedVideo':False,
    },timeout=600)
    response.raise_for_status(); items=response.json()
    by={i.get('shortCode') or code(i.get('inputUrl','')):i for i in items}
    rows=[]
    for queue_row,url in SOURCES.items():
        item=by.get(code(url),{})
        rows.append({
            'queue_row':queue_row,
            'url':url,
            'found':bool(item),
            'creator':item.get('ownerUsername',''),
            'creator_name':item.get('ownerFullName',''),
            'caption':item.get('caption','') or '',
            'transcript':item.get('transcript','') or item.get('videoTranscript','') or '',
            'duration':item.get('videoDuration') or item.get('duration'),
            'displayUrl':item.get('displayUrl',''),
            'videoUrl':item.get('videoUrl',''),
        })
    (OUT/'holds.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print('found',sum(r['found'] for r in rows),'of',len(rows))
    for r in rows: print(r['queue_row'],'caption',len(r['caption']),'transcript',len(r['transcript']))
    return 0
if __name__=='__main__': raise SystemExit(main())
