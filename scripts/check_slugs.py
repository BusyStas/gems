import os, sys, importlib.util
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)
# Import the app module by path to avoid package import issues
spec = importlib.util.spec_from_file_location('app', os.path.join(ROOT, 'app.py'))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
app = getattr(app_module, 'app')
app.config.update({'TESTING': True, 'GEMDB_API_URL': 'https://api.preciousstone.info', 'GEMDB_API_KEY': ''})
client = app.test_client()
for slug in ['rose_quartz', 'rose-quartz', 'diamond']:
    r = client.get(f'/gems/gem/{slug}')
    print(slug, r.status_code)
    if r.status_code != 200:
        print('Body (first 400 chars):', r.get_data(as_text=True)[:400])
