from app import app
with app.test_client() as c:
    r = c.get('/labs')
    print('labs index status', r.status_code)
    print('contains GIA link?', b'/labs/gia' in r.data)
    r2 = c.get('/labs/gia')
    print('gia status', r2.status_code)
    print('gia page contains', b'GIA' in r2.data)
