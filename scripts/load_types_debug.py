import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)
from gems.routes.gems import load_gem_types

print('Loading gem types...')
res = load_gem_types()
print('Type:', type(res))
if isinstance(res, dict):
    print('Top-level keys:', list(res.keys())[:10])
    # Show whether Rose Quartz present
    found = False
    for k, v in res.items():
        if isinstance(v, list):
            for item in v:
                if isinstance(item, str) and item.strip().lower() == 'rose quartz':
                    found = True
    print('Rose Quartz present?', found)
else:
    print(res)
