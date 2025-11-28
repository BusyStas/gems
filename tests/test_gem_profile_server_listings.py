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

    import importlib
    mods = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(mods.requests, 'get', fake_get)
    # Also ensure the route's local reference to get_gems_from_api returns Diamond
    import importlib
    gems_gems_module = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(gems_gems_module, 'get_gems_from_api', lambda limit=1000: [{'gem_type_name': 'Diamond'}])
    client = app.test_client()
    res = client.get('/gems/gem/diamond')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    # Ensure server-side listing was rendered (id and title present)
    assert '12345' in body
    assert 'Test Gem' in body


def test_server_side_empty_listings(monkeypatch):
    """When server returns an empty 'items' array, the page should not attempt client-side API fetch."""
    app = apppkg.app
    app.config.update({'TESTING': True, 'GEMDB_API_URL': 'https://api.preciousstone.info', 'GEMDB_API_KEY': ''})

    def fake_get(url, params=None, headers=None, timeout=10):
        class Resp:
            def __init__(self, payload):
                self.status_code = 200
                self._payload = payload
            def json(self):
                return self._payload

        if url.rstrip('/').endswith('/api/v1/gems') or url.rstrip('/').endswith('/api/v1/gems/'):
            # return a list as expected by get_gems_from_api
            return Resp([{'gem_type_name': 'Diamond'}])
        # listings endpoint
        return Resp({'items': []})

    import importlib
    mods = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(mods.requests, 'get', fake_get)
    import importlib
    gems_gems_module = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(gems_gems_module, 'get_gems_from_api', lambda limit=1000: [{'gem_type_name': 'Diamond'}])
    client = app.test_client()
    res = client.get('/gems/gem/diamond')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert 'No listings found.' in body


def test_server_filtered_by_gem(monkeypatch):
    """Server should request filtered listings and render different items per gem param"""
    app = apppkg.app
    app.config.update({'TESTING': True, 'GEMDB_API_URL': 'https://api.preciousstone.info', 'GEMDB_API_KEY': ''})

    def fake_get(url, params=None, headers=None, timeout=10):
        # Return different payloads depending on the gem filter
        gem = None
        if params:
            gem = params.get('gem') or params.get('gem_type_id')
        # if the URL is the base gems endpoint, return a list
        if url.rstrip('/').endswith('/api/v1/gems') or url.rstrip('/').endswith('/api/v1/gems/'):
            return type('R', (), {'status_code': 200, 'json': lambda self: [{'gem_type_name': 'Diamond'}, {'gem_type_name': 'Ruby'}]})()
        if gem and str(gem).lower().startswith('diamond'):
            return type('R', (), {'status_code': 200, 'json': lambda self: {'items': [{'id': 111, 'listing_title': 'Diamond One'}]}})()
        elif gem and str(gem).lower().startswith('ruby'):
            return type('R', (), {'status_code': 200, 'json': lambda self: {'items': [{'id': 222, 'listing_title': 'Ruby One'}]}})()
        # fallback empty
        return type('R', (), {'status_code': 200, 'json': lambda self: {'items': []}})()

    import importlib
    mods = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(mods.requests, 'get', fake_get)
    import importlib
    gems_gems_module = importlib.import_module('gems.routes.gems')
    # ensure the module's slug mapping works; patch get_gems_from_api to return both gems
    monkeypatch.setattr(gems_gems_module, 'get_gems_from_api', lambda limit=1000: [{'gem_type_name': 'Diamond'}, {'gem_type_name': 'Ruby'}])

    client = app.test_client()
    r1 = client.get('/gems/gem/diamond')
    assert r1.status_code == 200
    assert 'Diamond One' in r1.get_data(as_text=True)

    r2 = client.get('/gems/gem/ruby')
    assert r2.status_code == 200
    assert 'Ruby One' in r2.get_data(as_text=True)
