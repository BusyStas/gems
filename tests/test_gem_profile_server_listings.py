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


def test_server_renders_links_with_no_referrer(monkeypatch):
    """Ensure server-rendered listing links include no-referrer attributes and rel as required."""
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
            return Resp([{'gem_type_name': 'Diamond'}])
        # listings endpoint - return a single listing to be rendered by the server
        return Resp({'items': [{'id': 999, 'weight': 2.3, 'price': 123.4, 'listing_title': 'NoRef Test', 'seller_nickname': 'NoRefSeller'}]})

    import importlib
    mods = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(mods.requests, 'get', fake_get)
    # Also ensure the route's local reference to get_gems_from_api returns Diamond
    monkeypatch.setattr(mods, 'get_gems_from_api', lambda limit=1000: [{'gem_type_name': 'Diamond'}])
    client = app.test_client()
    res = client.get('/gems/gem/diamond')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    # Assert the title anchor has the rel and referrerpolicy attributes
    assert 'rel="noopener noreferrer"' in body
    assert 'referrerpolicy="no-referrer"' in body


def test_gauge_is_narrow_and_centered(monkeypatch):
    """Verify that the gauge has a narrow max-width defined in CSS to avoid taking full column width."""
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
            return Resp([{'gem_type_name': 'Diamond'}])
        return Resp({'items': []})

    import importlib
    mods = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(mods.requests, 'get', fake_get)
    monkeypatch.setattr(mods, 'get_gems_from_api', lambda limit=1000: [{'gem_type_name': 'Diamond'}])
    client = app.test_client()
    res = client.get('/gems/gem/diamond')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    # Check that CSS contains the max-width in-lined rule for gauge
    assert 'max-width: 260px' in body


def test_table_colgroup_and_title_nowrap(monkeypatch):
    """Verify that the table includes a colgroup with fixed width and that title anchors have `listing-title-link` class."""
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
            return Resp([{'gem_type_name': 'Diamond'}])
        # listings endpoint: return an item
        return Resp({'items': [{'id': 55, 'weight': 2.01, 'price': 5, 'listing_title': 'Long Title For Test', 'seller_nickname': 'SSeller'}]})

    import importlib
    mods = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(mods.requests, 'get', fake_get)
    monkeypatch.setattr(mods, 'get_gems_from_api', lambda limit=1000: [{'gem_type_name': 'Diamond'}])
    client = app.test_client()
    res = client.get('/gems/gem/diamond')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    # colgroup presence and widths and profile-bottom container
    assert '<colgroup>' in body
    assert 'class="profile-bottom"' in body
    assert 'style="width: 80px;"' in body
    assert 'class="listing-title-link"' in body


def test_profile_bottom_is_inside_grid(monkeypatch):
    """Ensure `profile-bottom` is located inside `profile-grid` (i.e., profile-grid tag appears before profile-bottom)."""
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
            return Resp([{'gem_type_name': 'Diamond'}])
        return Resp({'items': []})

    import importlib
    mods = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(mods.requests, 'get', fake_get)
    monkeypatch.setattr(mods, 'get_gems_from_api', lambda limit=1000: [{'gem_type_name': 'Diamond'}])
    client = app.test_client()
    res = client.get('/gems/gem/diamond')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert body.find('class="profile-grid"') < body.find('class="profile-bottom"')


def test_profile_right_is_sibling_not_nested(monkeypatch):
    """Ensure that `profile-right` is a sibling of `profile-left` (closing tag for left appears before right)."""
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
            return Resp([{'gem_type_name': 'Diamond'}])
        return Resp({'items': []})

    import importlib
    mods = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(mods.requests, 'get', fake_get)
    monkeypatch.setattr(mods, 'get_gems_from_api', lambda limit=1000: [{'gem_type_name': 'Diamond'}])
    client = app.test_client()
    res = client.get('/gems/gem/diamond')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    # closing div for left column should appear just before opening of right
    assert '</div>\n\n      <div class="profile-right">' in body or '</div>\n      <div class="profile-right">' in body


def test_listings_hidden_when_not_signed_in(monkeypatch):
    """Ensure that when user isn't signed in, the listings table is not shown and a sign-in message is shown instead."""
    from types import SimpleNamespace
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
            return Resp([{'gem_type_name': 'Diamond'}])
        return Resp({'items': [{'id': 101, 'weight': 1.1, 'price': 100, 'listing_title': 'Test', 'seller_nickname': 'Seller'}]})

    import importlib
    mods = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(mods.requests, 'get', fake_get)
    monkeypatch.setattr(mods, 'get_gems_from_api', lambda limit=1000: [{'gem_type_name': 'Diamond'}])
    # Simulate not logged in user
    monkeypatch.setattr(mods, 'current_user', SimpleNamespace(is_authenticated=False, google_id=None))
    client = app.test_client()
    res = client.get('/gems/gem/diamond')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert 'Please sign in to view current listings.' in body
    assert '<table id="current-listings"' not in body


def test_listings_visible_when_signed_in(monkeypatch):
    """Ensure that when a user is signed in, the listings table is shown and contains items."""
    from types import SimpleNamespace
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
            return Resp([{'gem_type_name': 'Diamond'}])
        return Resp({'items': [{'id': 202, 'weight': 2.5, 'price': 500.0, 'listing_title': 'Diamond Listing', 'seller_nickname': 'SellerX'}]})

    import importlib
    mods = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(mods.requests, 'get', fake_get)
    monkeypatch.setattr(mods, 'get_gems_from_api', lambda limit=1000: [{'gem_type_name': 'Diamond'}])
    # Simulate logged in user
    monkeypatch.setattr(mods, 'current_user', SimpleNamespace(is_authenticated=True, google_id='u123'))
    client = app.test_client()
    res = client.get('/gems/gem/diamond')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert '<table id="current-listings"' in body
    assert 'Diamond Listing' in body


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
