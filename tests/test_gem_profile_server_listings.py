import sys
sys.path.insert(0, r'd:\OneDrive\Documents\GitHub')
from gems import app as apppkg
from types import SimpleNamespace


def test_server_side_listings(monkeypatch):
    app = apppkg.app
    app.config.update({'TESTING': True, 'GEMDB_API_URL': 'https://api.preciousstone.info', 'GEMDB_API_KEY': ''})

    def fake_get(url, params=None, headers=None, timeout=10):
        class Resp:
            status_code = 200

            def __init__(self, payload):
                self._payload = payload

            def json(self):
                return self._payload

        if url.rstrip('/').endswith('/api/v1/gems') or url.rstrip('/').endswith('/api/v1/gems/'):
            return Resp([{'gem_type_name': 'Diamond'}])
        # listings endpoint
        return Resp({'items': [{'id': 12345, 'weight': 1.2, 'price': 99.9, 'listing_title': 'Test Gem', 'seller_nickname': 'tester'}]})

    monkeypatch.setattr('requests.get', fake_get)
    # Also ensure the route's local reference to get_gems_from_api returns Diamond
    import importlib
    gems_gems_module = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(gems_gems_module, 'get_gems_from_api', lambda limit=1000: [{'gem_type_name': 'Diamond'}])
    # Also patch the api client to provide a list of gem types so the slug resolves
    monkeypatch.setattr('utils.api_client', 'get_gems_from_api', lambda limit=1000: [{'gem_type_name': 'Diamond'}])
    client = app.test_client()
    res = client.get('/gems/gem/diamond')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    # Ensure server-side listing was rendered (id and title present)
    assert '12345' in body
    assert 'Test Gem' in body
