# Quick helper to test routes without running a server
from gems import app as apppkg

def check(path):
    app = apppkg.app
    app.config.update({'TESTING': True})
    client = app.test_client()
    resp = client.get(path)
    print('STATUS:', resp.status_code)
    data = resp.get_data(as_text=True)
    print('LEN:', len(data))
    print(data[:2000])

if __name__ == '__main__':
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else '/privacy'
    check(p)
