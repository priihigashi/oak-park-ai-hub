"""OPC filing through the existing SHEETS_TOKEN route; header-based, read back.

No new OAuth scopes/secret conventions, no sharing changes, no destructive edits.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import mimetypes
from pathlib import Path
import re

from opc_contract import GateError, STATUS, find_duplicates, photo_eligible, slug, tracker_row

CONTROL = '1C1CAZ8lSgeVLSSCYIg-D9XPJcSLHyIOh1okKtvhZZQg'
CONTROL_TAB = '🎬 In Production'
CAROUSEL_PARENT = '16P2JN74JAAW3HKnmNqPGPrAq7N5jDNii'
FORMATS = '1XqXSyJC_iHMTrmMxpM5ZR7S-WQxz19HhDJO1HomdncM'
IDEAS = '1CrVHlIe8u1bo_1W0iU0O3WKv2JUrm0-UO76y4p5NC_c'
PHOTO_TRACKER = '1d8bLR-JHUEbKB9D7cpQ2B97xpJvnCxJoPljVTmMj1i4'
FLOW = '1fggy918FgPfnMQ-dzGQk2zx9uhi2_-uWXMKGW4MA47k'


def quote_tab(tab: str) -> str:
    return "'" + tab.replace("'", "''") + "'"


def dictionary_rows(rows: list[list]) -> list[dict]:
    if not rows:
        return []
    return [dict(zip(rows[0], row + ['']*(len(rows[0])-len(row)))) for row in rows[1:] if any(row)]


class Store:
    def __init__(self):
        from googleapiclient.discovery import build
        from capture_pipeline import _get_creds
        creds = _get_creds(['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/spreadsheets'])
        self.drive = build('drive','v3',credentials=creds,cache_discovery=False)
        self.sheets = build('sheets','v4',credentials=creds,cache_discovery=False)
        self.docs = build('docs','v1',credentials=creds,cache_discovery=False)

    def read_rows(self, sheet: str, tab: str, end_col: str, max_rows: int = 5000) -> list[list]:
        meta = self.sheets.spreadsheets().get(spreadsheetId=sheet,fields='sheets.properties').execute()
        matches = [x['properties'] for x in meta['sheets'] if x['properties']['title'] == tab]
        if len(matches) != 1:
            raise GateError('Required spreadsheet tab is unavailable')
        count = matches[0]['gridProperties']['rowCount']
        if count > max_rows:
            raise GateError('Sheet exceeds inspected range budget; do not silently use a partial dedupe read')
        a1 = f'{quote_tab(tab)}!A1:{end_col}{count}'
        return self.sheets.spreadsheets().values().get(spreadsheetId=sheet,range=a1).execute().get('values',[])

    def preflight(self) -> dict:
        parent = self.drive.files().get(fileId=CAROUSEL_PARENT,fields='id,mimeType,driveId,capabilities',supportsAllDrives=True).execute()
        if parent['mimeType'] != 'application/vnd.google-apps.folder' or not parent.get('driveId'):
            raise GateError('OPC carousel parent is not the expected shared-drive folder')
        if not parent.get('capabilities',{}).get('canAddChildren'):
            raise GateError('No permission to file into the OPC carousel folder')
        rows = self.read_rows(CONTROL,CONTROL_TAB,'M')
        tracker_row(rows[0],{'Status':STATUS})
        doc = self.docs.documents().get(documentId=FORMATS).execute()
        if 'FORMAT-030' not in json.dumps(doc,ensure_ascii=False):
            raise GateError('Existing FORMAT-030 registry entry is unavailable')
        flow = self.read_rows(FLOW,'All Docs','I')
        expected = {'NAME','TYPE','NICHE','STATUS','DESCRIPTION','OPEN','DOC_ID','TABS','LAST UPDATED'}
        if not flow or set(flow[0]) != expected:
            raise GateError('Flow Plans header changed; no paid generation started')
        return {'tracker':rows,'format':'FORMAT-030 / OPC visual feed + private PRINT proof'}

    def duplicates(self, title: str, keys: list[str], url: str, rebuild_row: int = 0) -> list[int]:
        rows = self.read_rows(CONTROL,CONTROL_TAB,'M')
        found = find_duplicates(rows,title,keys,url)
        if rebuild_row:
            if rebuild_row not in found:
                raise GateError('Requested rebuild row does not match the source/topic')
            found = [n for n in found if n != rebuild_row]
        return found

    def ideas(self) -> list[dict]:
        rows = self.read_rows(IDEAS,'Content Ideas','E')
        records = dictionary_rows(rows)
        relevant = re.compile(r'kitchen|countertop|granite|quartz|renovat|remodel|concrete|porch|cove.*led|contractor|permit|paver|bathroom',re.I)
        primary = [r for r in records if relevant.search(json.dumps(r))]
        def date_key(row):
            text=str(row.get('Date',''))
            for fmt in ('%m/%d/%Y','%Y-%m-%d','%d/%m/%Y'):
                try:return datetime.strptime(text,fmt)
                except ValueError:pass
            return datetime.min
        primary.sort(key=date_key,reverse=True)
        open_rows = self.read_rows(IDEAS,'OPEN IDEAS','Z')[5:]
        secondary = [r for r in dictionary_rows(open_rows) if relevant.search(json.dumps(r))]
        return ([{'priority':1,'source_tab':'Content Ideas',**r} for r in primary[:15]]
                +[{'priority':2,'source_tab':'OPEN IDEAS',**r} for r in secondary[:20]])

    def photos(self, project_group: str) -> list[dict]:
        rows = self.read_rows(PHOTO_TRACKER,'READY_FOR_WEB','Q',max_rows=500)
        return [r for r in dictionary_rows(rows) if photo_eligible(r) and r['Project / Property Grouping'] == project_group]

    def list_children(self, parent: str) -> list[dict]:
        result, token = [], None
        while True:
            data = self.drive.files().list(q=f"'{parent}' in parents and trashed=false",pageSize=1000,pageToken=token,
                fields='nextPageToken,files(id,name,mimeType,appProperties,webViewLink)',supportsAllDrives=True,includeItemsFromAllDrives=True).execute()
            result.extend(data.get('files',[]));token=data.get('nextPageToken')
            if not token:
                return result

    def folder(self, name: str, parent: str, run_key: str = '') -> dict:
        body = {'name':name,'mimeType':'application/vnd.google-apps.folder','parents':[parent]}
        if run_key:
            body['appProperties'] = {'opcPrintRun':run_key,'state':'STARTED_NOT_APPROVED'}
        return self.drive.files().create(body=body,fields='id,name,webViewLink',supportsAllDrives=True).execute()

    def start_run(self, title: str, run_key: str) -> dict:
        """Persistent once-only guard survives an Actions rerun of paid validation."""
        children = self.list_children(CAROUSEL_PARENT)
        if any(f.get('appProperties',{}).get('opcPrintRun') == run_key for f in children):
            raise GateError('This run key already exists in Drive; no duplicate billed run or row was started')
        versions = [int(m.group(1)) for f in children if (m:=re.match(r'v(\d+)_',f['name']))]
        return self.folder(f'v{max(versions,default=0)+1}_{slug(title)}_print',CAROUSEL_PARENT,run_key)

    def upload(self, path: Path, parent: str) -> dict:
        from googleapiclient.http import MediaFileUpload
        result = self.drive.files().create(body={'name':path.name,'parents':[parent]},
            media_body=MediaFileUpload(str(path),mimetype=mimetypes.guess_type(path.name)[0] or 'application/octet-stream',resumable=True),
            fields='id,name,webViewLink,md5Checksum,size',supportsAllDrives=True).execute()
        check = self.drive.files().get(fileId=result['id'],fields='id,md5Checksum,size,parents,webViewLink',supportsAllDrives=True).execute()
        if int(check.get('size',-1)) != path.stat().st_size or check.get('md5Checksum') != hashlib.md5(path.read_bytes()).hexdigest():
            raise GateError('Drive upload readback checksum/size mismatch')
        return check

    def download_photo(self, row: dict, target: Path) -> None:
        if not photo_eligible(row):
            raise GateError('Unapproved photo')
        from googleapiclient.http import MediaIoBaseDownload
        m = re.fullmatch(r'https://drive\.google\.com/file/d/([\w-]+)/view(?:\?.*)?',row['Selected Copy Drive Location'])
        if not m:
            raise GateError('Unsupported approved photo location')
        request = self.drive.files().get_media(fileId=m.group(1),supportsAllDrives=True)
        with target.open('wb') as stream:
            dl = MediaIoBaseDownload(stream,request);done=False
            while not done:
                _,done=dl.next_chunk()

    def upload_tree(self, root: Path, folder: dict) -> dict:
        # This folder belongs to this run. Reuse only our own already uploaded paths.
        parents = {'.':folder['id']};links={}
        for path in sorted(root.rglob('*')):
            rel=path.relative_to(root)
            if path.is_dir():
                existing=[f for f in self.list_children(parents[str(rel.parent)]) if f['name']==path.name and f['mimeType']=='application/vnd.google-apps.folder']
                parents[str(rel)] = (existing[0] if existing else self.folder(path.name,parents[str(rel.parent)]))['id']
            elif path.is_file() and path.suffix not in ('.woff','.woff2','.ttf','.otf'):
                links[str(rel)] = self.upsert_run_file(path,parents[str(rel.parent)])['webViewLink']
        return links

    def upsert_run_file(self, path: Path, parent: str) -> dict:
        """Only called inside the newly created, run-owned version folder."""
        matches=[f for f in self.list_children(parent) if f['name']==path.name]
        if len(matches)>1:raise GateError('Duplicate run-owned artifact names; refusing ambiguous update')
        if not matches:return self.upload(path,parent)
        from googleapiclient.http import MediaFileUpload
        file=matches[0]
        result=self.drive.files().update(fileId=file['id'],
            media_body=MediaFileUpload(str(path),mimetype=mimetypes.guess_type(path.name)[0] or 'application/octet-stream',resumable=True),
            fields='id,webViewLink,md5Checksum,size',supportsAllDrives=True).execute()
        check=self.drive.files().get(fileId=file['id'],fields='id,webViewLink,md5Checksum,size',supportsAllDrives=True).execute()
        if check.get('md5Checksum')!=hashlib.md5(path.read_bytes()).hexdigest() or int(check.get('size',-1))!=path.stat().st_size:
            raise GateError('Run artifact replacement readback failed')
        return check

    def append_verified(self, sheet: str, tab: str, row: list[str]) -> str:
        result = self.sheets.spreadsheets().values().append(spreadsheetId=sheet,range=f'{quote_tab(tab)}!A1',
            valueInputOption='RAW',insertDataOption='INSERT_ROWS',body={'values':[row]}).execute()
        updated = result.get('updates',{}).get('updatedRange','')
        if not updated or not updated.startswith(quote_tab(tab)+'!') and not updated.startswith(tab+'!'):
            raise GateError('Sheets did not return a tab-qualified updatedRange')
        got = self.sheets.spreadsheets().values().get(spreadsheetId=sheet,range=updated).execute().get('values',[[]])[0]
        got = [str(x) for x in got] + ['']*(len(row)-len(got))
        if got != row:
            raise GateError('Sheets row readback did not match the write')
        return updated

    def file_row(self, spec: dict, folder: dict, links: dict) -> str:
        rows = self.read_rows(CONTROL,CONTROL_TAB,'M')
        headers = rows[0]
        link_col = headers.index('Drive Folder Link')
        if any(len(r)>link_col and r[link_col] == folder['webViewLink'] for r in rows[1:]):
            raise GateError('This output folder already has a content row')
        data = {'# Reviews':'0','Title':spec['title'],'Post Type':'Homeowner education','Format':'FORMAT-030 OPC visual PRINT',
                'Content Type':'Carousel','Status':STATUS,'Drive Folder Link':folder['webViewLink'],
                'Caption':spec['caption'],'Hashtags':spec.get('hashtags',''),'Output Link':links['review.html'],
                'Date Created':datetime.now(timezone.utc).date().isoformat(),'Research Doc Link':links['resources/evidence.json'],
                'Original Source Video Link':spec.get('source_url','')}
        return self.append_verified(CONTROL,CONTROL_TAB,tracker_row(headers,data))

    def flow_row(self, spec: dict, folder: dict, links: dict) -> str:
        rows = self.read_rows(FLOW,'All Docs','I')
        required = {'NAME','TYPE','NICHE','STATUS','DESCRIPTION','OPEN','DOC_ID','TABS','LAST UPDATED'}
        if not rows or set(rows[0]) != required:
            raise GateError('Flow Plans header changed; refusing a guessed write')
        values = {'NAME':'OPC PRINT — '+spec['title'],'TYPE':'Content review','NICHE':'OPC','STATUS':'READY FOR PRISCILA REVIEW',
                  'DESCRIPTION':'Visual feed, private proof pack, usage ledger; not approved or published.',
                  'OPEN':links['review.html'],'DOC_ID':folder['id'],'TABS':'',
                  'LAST UPDATED':datetime.now(timezone.utc).date().isoformat()}
        return self.append_verified(FLOW,'All Docs',[values.get(h,'') for h in rows[0]])

    def rename_run(self, folder: dict, title: str) -> None:
        prefix=re.match(r'v[0-9]+_',folder['name'])
        if not prefix:raise GateError('Only the current version folder may be renamed')
        name=prefix[0]+slug(title)+'_print'
        result=self.drive.files().update(fileId=folder['id'],body={'name':name},fields='id,name',supportsAllDrives=True).execute()
        folder['name']=result['name']

    def finish(self, folder: dict, state: str) -> None:
        old=self.drive.files().get(fileId=folder['id'],fields='appProperties',supportsAllDrives=True).execute().get('appProperties',{})
        self.drive.files().update(fileId=folder['id'],body={'appProperties':{**old,'state':state}},fields='id,appProperties',supportsAllDrives=True).execute()
