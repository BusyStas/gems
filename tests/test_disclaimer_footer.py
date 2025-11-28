import pytest
from gems import app as apppkg


def test_disclaimer_present_on_homepage(monkeypatch):
    app = apppkg.app
    app.config.update({'TESTING': True})
    client = app.test_client()
    res = client.get('/')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert 'Disclaimer' in body
    # Check links (short aliases preferred)
    assert '/privacy' in body
    assert '/terms' in body
    assert 'support@preciousstone.info' in body


def test_disclaimer_present_on_gem_profile(monkeypatch):
    app = apppkg.app
    app.config.update({'TESTING': True})
    # monkeypatch requests to avoid external calls
    def fake_get(url, params=None, headers=None, timeout=10):
        class R:
            status_code = 200
            def json(self):
                return []
        return R()
    import importlib
    gems_routes = importlib.import_module('gems.routes.gems')
    monkeypatch.setattr(gems_routes.requests, 'get', fake_get)

    client = app.test_client()
    res = client.get('/gems/gem/diamond')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert 'Disclaimer' in body
    assert '/privacy' in body
    assert '/terms' in body
    assert 'support@preciousstone.info' in body


def test_privacy_route():
    app = apppkg.app
    app.config.update({'TESTING': True})
    client = app.test_client()
    res = client.get('/privacy')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert 'Privacy Policy' in body
    assert 'support@preciousstone.info' in body


def test_privacy_alias_route():
    app = apppkg.app
    app.config.update({'TESTING': True})
    client = app.test_client()
    res = client.get('/privacy')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert 'Privacy Policy' in body


def test_terms_route():
    app = apppkg.app
    app.config.update({'TESTING': True})
    client = app.test_client()
    res = client.get('/terms')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert 'Terms of Service' in body
    assert 'support@preciousstone.info' in body


def test_terms_alias_route():
    app = apppkg.app
    app.config.update({'TESTING': True})
    client = app.test_client()
    res = client.get('/terms')
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert 'Terms of Service' in body
