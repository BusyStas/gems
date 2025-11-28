import sys
sys.path.insert(0, r'd:\OneDrive\Documents\GitHub')
from importlib import import_module
import requests

# Prepare fakery
class Resp:
    def __init__(self,p):
        self.status_code = 200
        self._p = p
    def json(self):
        return self._p

def fake_get(url, params=None, headers=None, timeout=10):
    print('FAKE_GET URL', url)
    print('PARAMS:', params)
    if url.rstrip('/').endswith('/api/v1/gems'):
        return Resp([{'gem_type_name': 'Diamond'}, {'gem_type_name': 'Ruby'}, {'gem_type_name': 'Rose Quartz'}])
    if url.rstrip('/').endswith('/api/v1/listings-view/filtered'):
        gem = params.get('gem') or params.get('gem_type_id')
        if gem and str(gem).lower().startswith('diamond'):
            return Resp({'items':[{'id':111,'listing_title':'Diamond One'}]})
        if gem and str(gem).lower().startswith('ruby'):
            return Resp({'items':[{'id':222,'listing_title':'Ruby One'}]})
        if gem and str(gem).lower().startswith('rose'):
            return Resp({'items':[{'id':333,'listing_title':'Rose One'}]})
    return Resp({'items':[]})

# Patch both utils and module-level requests
m_routes = import_module('gems.routes.gems')
import utils.api_client as api_client

api_client.requests.get = fake_get
m_routes.requests.get = fake_get

# Also patch module get_gems_from_api
m_routes.get_gems_from_api = lambda limit=1000: [{'gem_type_name': 'Diamond'}, {'gem_type_name': 'Ruby'}, {'gem_type_name':'Rose Quartz'}]

from gems import app as apppkg
app = apppkg.app
app.config.update({'TESTING': True, 'GEMDB_API_URL': 'https://api.preciousstone.info', 'GEMDB_API_KEY': ''})
client = app.test_client()

for slug in ['diamond','ruby','rose-quartz']:
    r = client.get(f'/gems/gem/{slug}')
    print('Slug:', slug, 'Status:', r.status_code)
    body = r.get_data(as_text=True)
    if r.status_code == 200:
        # find listing ids
        import re
        ids = re.findall(r'<td>(\d+)</td>', body)
        print('IDs in body:', ids[:5])
    else:
        print('Error page length', len(body))
