import sys
sys.path.insert(0, r'd:\OneDrive\Documents\GitHub')
from importlib import import_module
import requests

class Resp:
    status_code = 200
    def __init__(self, p):
        self._p = p
    def json(self):
        return self._p

def fake_get(url, params=None, headers=None, timeout=10):
    print('FAKE_GET URL', url)
    print('PARAMS:', params)
    return Resp({'items': []})

requests.get = fake_get
m = import_module('gems.routes.gems')
setattr(m, 'get_gems_from_api', lambda limit=1000: [{'gem_type_name':'Diamond'}])

from gems import app as apppkg
app = apppkg.app
app.config.update({'TESTING': True, 'GEMDB_API_URL':'https://api.preciousstone.info', 'GEMDB_API_KEY':''})
client = app.test_client()
res = client.get('/gems/gem/diamond')
print('Status:', res.status_code)
print(res.get_data(as_text=True)[:800])
