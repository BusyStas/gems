import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, 'gems')))
import importlib

# load app module directly to avoid package import issues
import importlib
gems_app_module = importlib.import_module('gems.app')
app = gems_app_module.app

# Setup fake_get similar to tests
class Resp:
    def __init__(self, p):
        self.status_code = 200
        self._p = p
    def json(self):
        return self._p

def fake_get(url, params=None, headers=None, timeout=10):
    print('FAKE GET URL', url)
    if url.rstrip('/').endswith('/api/v1/gems'):
        return Resp([{'gem_type_name': 'Diamond'}])
    return Resp({'items': []})

# Patch module
mods = importlib.import_module('gems.routes.gems')
mods.requests.get = fake_get
mods.get_gems_from_api = lambda limit=1000: [{'gem_type_name':'Diamond'}]
mods.current_user = type('CU', (), {'is_authenticated': False, 'google_id': None})()
print('mods.current_user', mods.current_user, type(mods.current_user), getattr(mods.current_user, 'is_authenticated', None), getattr(mods.current_user, 'google_id', None))

app.config.update({'TESTING': True, 'GEMDB_API_URL': 'https://api.preciousstone.info', 'GEMDB_API_KEY': ''})
client = app.test_client()
r = client.get('/gems/gem/diamond')
print('Status', r.status_code)
body = r.get_data(as_text=True)
print('Len', len(body))
# Print a small section around profile-left/ right
ix = body.find('<div class="profile-left">')
if ix >=0:
    print(body[ix:ix+2000])
boundary_idx_left_close = body.find('</div>', ix)
boundary_idx_right_open = body.find('<div class="profile-right"', ix)
print('Left close idx', boundary_idx_left_close, 'Right open idx', boundary_idx_right_open)
if boundary_idx_left_close >=0 and boundary_idx_right_open >=0:
    seg = body[boundary_idx_left_close:boundary_idx_right_open+40]
    print('boundary segment repr:', repr(seg))
    print('boundary segment:', seg)

print('\n\nJS showListings var:')
start = body.find('const showListings = ')
if start>=0:
    print(body[start:start+80])

# Print whether colgroup present
print('\ncolgroup present?', '<colgroup>' in body)
# Print table presence
print('\ncurrent-listings table present?', '<table id="current-listings"' in body)
