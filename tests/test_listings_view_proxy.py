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


def test_title_and_seller_url_synthesis_and_price(monkeypatch):
    """The proxy should synthesize product and seller URLs and format price if necessary"""
    captured = {}

    def fake_get(url, params=None, headers=None, timeout=None):
        captured['url'] = url
        captured['params'] = params or {}
        class FakeResp:
            status_code = 200
            def json(self):
                return {'items': [{'id': 123, 'weight': '0.85', 'price': 100, 'listing_title': 'Test Gem! & Other', 'seller_nickname': 'John Smith', 'listing_url': None, 'seller_profile': None, 'gem_type_name': 'Ruby'}]}
        return FakeResp()

    monkeypatch.setattr(requests, 'get', fake_get)
    from app import app
    client = app.test_client()
    resp = client.get('/api/v1/listings-view/?gem=Ruby')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'items' in data
    item = data['items'][0]
    assert item.get('listing_id') == 123
    assert item.get('carat_weight') == '0.85' or float(item.get('carat_weight')) == 0.85
    # title_url should be synthesized with slugified title and id
    assert item.get('title_url') == 'https://www.gemrockauctions.com/products/test-gem-other-123'
    # seller_url should be synthesized
    assert item.get('seller_url') == 'https://www.gemrockauctions.com/stores/john-smith'
    # price should be formatted with $ and two decimals
    assert item.get('price') == '$100.00'
