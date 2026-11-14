#!/usr/bin/env python3
"""Sync authorized private export to its review sheet; never log rows or tokens."""
import json
import os
import urllib.parse
import urllib.request
from sheet_append_row import get_token

HEADERS = ['ID do envio','Recebido em','Ponto do site','Artigo','Sugestão avaliada','Avaliação','Tipo de mensagem','Mensagem','Link da fonte','Nome (opcional)','Instagram (opcional)','E-mail (opcional)','Situação da revisão','Análise da página','Atualizado em','Versão do site']

def fetch_json(url, token, body=None):
    headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    request = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)

def oidc_token():
    endpoint = os.environ['ACTIONS_ID_TOKEN_REQUEST_URL'] + '&audience=plp299-private-sheet-sync'
    result = fetch_json(endpoint, os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN'])
    return result['value']

def sheet_call(sheet_id, suffix, token, body=None):
    return fetch_json('https://sheets.googleapis.com/v4/spreadsheets/' + sheet_id + suffix, token, body)

def ensure_tab(sheet_id, tab, google):
    metadata = sheet_call(sheet_id, '?fields=sheets(properties(title))', google)
    if tab not in [s['properties']['title'] for s in metadata['sheets']]:
        sheet_call(sheet_id, ':batchUpdate', google, {'requests':[{'addSheet':{'properties':{'title':tab}}}]})

def append_missing(sheet_id, tab, rows, google):
    quoted = "'" + tab.replace("'", "''") + "'"
    range_a = urllib.parse.quote(quoted + '!A:A', safe='')
    current = sheet_call(sheet_id, '/values/' + range_a, google).get('values', [])
    known = {r[0] for r in current if r}
    additions = []
    if not current:
        additions.append(HEADERS)
    for row in rows:
        if row[0] not in known:
            additions.append(row)
            known.add(row[0])
    if additions:
        target = urllib.parse.quote(quoted + '!A:P', safe='')
        result = sheet_call(sheet_id, '/values/' + target + ':append?valueInputOption=RAW&insertDataOption=INSERT_ROWS', google, {'values':additions})
        assert result.get('updates', {}).get('updatedRows') == len(additions)
    return len(additions)

def main():
    origin = os.environ.get('REVIEW_ORIGIN', 'https://plp299-nota-aos-deputados.vercel.app')
    assert origin.startswith('https://') and '/' not in origin[8:]
    google = get_token()
    identity = oidc_token()
    count = 0
    for test in [False, True]:
        cursor = None
        seen = set()
        while True:
            export = fetch_json(origin + '/api/review/export', identity, {'test':test, 'cursor':cursor})
            tab = 'Testes de integração' if test else 'Respostas'
            ensure_tab(export['sheetId'], tab, google)
            count += append_missing(export['sheetId'], tab, export['rows'], google)
            cursor = export.get('cursor')
            if not cursor:
                break
            if cursor in seen:
                raise RuntimeError('Cursor repetido; sincronização interrompida.')
            seen.add(cursor)
    print(json.dumps({'sync':'confirmed','appendedRows':count,'personalDataLogged':False}))

if __name__ == '__main__':
    main()
