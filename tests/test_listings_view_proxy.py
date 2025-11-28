import json
import requests
from flask import url_for


def test_google_user_id_forwarded(monkeypatch):
    captured = {}

    def fake_get(url, params=None, headers=None, timeout=None):
        captured['url'] = url
        captured['params'] = params or {}
        class FakeResp:
            status_code = 200
            def json(self):
                return {'items': [{'id': 1, 'weight': 2.0, 'price': 100, 'listing_title': 'Test', 'seller_nickname': 'Seller', 'listing_url': 'http://example.com/1', 'gem_type_name': 'Ruby'}]}
        return FakeResp()

    # patch requests.get used by the proxy
    monkeypatch.setattr(requests, 'get', fake_get)
    from app import app
    client = app.test_client()
    resp = client.get('/api/v1/listings-view/?gem=Ruby&google_user_id=abc123')
    assert resp.status_code == 200
    # the proxy should forward google_user_id to upstream
    assert captured['params'].get('google_user_id') == 'abc123'
    data = json.loads(resp.data)
    assert 'items' in data
    item = data['items'][0]
    assert 'listing_id' in item
    assert 'carat_weight' in item
    assert 'title' in item
    assert 'seller' in item
    assert 'title_url' in item
