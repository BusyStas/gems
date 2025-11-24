from app import app

with app.test_client() as c:
    paths = ['/', '/gems/', '/gems/by-hardness', '/gems/by-price', '/gems/by-size', '/stores/gem-rock-auctions']
    for p in paths:
        r = c.get(p)
        print(p, r.status_code)
