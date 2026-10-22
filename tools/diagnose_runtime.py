# Copyright IBM Corp. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

"""Print selected runtime/actor diagnostics without printing tokens or secrets."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
cfg = {**dotenv_values(ROOT / '.env'), **os.environ}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def required(key):
    value = cfg.get(key, '')
    if not value or str(value).startswith('<'):
        raise SystemExit('Missing setting: ' + key)
    return value

def post(url, values):
    request = urllib.request.Request(url, data=urllib.parse.urlencode(values).encode(),
                                    headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=30) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        try:
            result = json.loads(error.read())
        except ValueError:
            result = {'error': 'Non-JSON response omitted'}
        return error.code, result
    except urllib.error.URLError as error:
        raise SystemExit('Transport error: ' + str(error.reason))

def show(label, status, value, keys):
    print(f'\n=== {label}: HTTP {status} ===')
    print(json.dumps({key: value[key] for key in keys if key in value}, indent=2))

print('Project:', ROOT)
print('Python:', sys.executable)
print(json.dumps({key: cfg.get(key, '') for key in [
    'AGENT_ID', 'ACTOR_CLIENT_ID', 'SUBJECT_CLIENT_ID', 'STS_CLIENT_ID',
    'VERIFY_TOKEN_ENDPOINT', 'VERIFY_INTROSPECTION_ENDPOINT', 'STS_AUDIENCE'
]}, indent=2))
agent_id = required('AGENT_ID')
status, token = post(required('VERIFY_TOKEN_ENDPOINT'), {
    'grant_type': 'client_credentials', 'client_id': required('ACTOR_CLIENT_ID'),
    'client_secret': required('ACTOR_CLIENT_SECRET'), 'scope': cfg.get('ACTOR_SCOPES', 'agent.run')})
show('ACTOR TOKEN', status, token, ['token_type', 'scope', 'expires_in', 'error', 'error_description'])
if status != 200 or not token.get('access_token'):
    raise SystemExit('Stop: actor acquisition failed')
status, claims = post(required('VERIFY_INTROSPECTION_ENDPOINT'), {
    'client_id': required('STS_CLIENT_ID'), 'client_secret': required('STS_CLIENT_SECRET'),
    'token': token['access_token'], 'token_type_hint': 'access_token'})
show('ACTOR INTROSPECTION', status, claims, [
    'active', 'sub', 'client_id', 'iss', 'aud', 'scope', 'iat', 'exp', 'error', 'error_description'])
if status != 200:
    raise SystemExit('Use an introspection-authorized client in the API collection; STS introspection was not permitted or failed.')
if claims.get('active') is not True or claims.get('sub') != agent_id:
    raise SystemExit('FAIL: active actor sub must equal registry AGENT_ID')
print('PASS: actor sub equals configured registry AGENT_ID')
print('Next: subject may_act.sub and delegated act.sub must match this AgentID for the supplied delegation path.')
