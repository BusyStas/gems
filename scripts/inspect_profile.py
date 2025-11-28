import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from app import app

app.testing = True
client = app.test_client()
rv = client.get('/gems/gem/diamond')
body = rv.get_data(as_text=True)

import re
pattern = re.compile(r'</div>\s*<div class="profile-right"', re.MULTILINE)
match = pattern.search(body)
if match:
	i1 = match.start()
	i2 = match.end()
	seg = body[i1-10:i2+10]
	print('Found match at', i1, i2)
	print('segment repr:')
	print(repr(seg))
	print('segment:')
	print(seg)
else:
	print('No match found for closing left / opening right')
	print('body head:')
	print(body[:2000])
from app import app

c = app.test_client()
r = c.get('/gems/gem/diamond')
b = r.get_data(as_text=True)
i1 = b.find('</div>')
i2 = b.find('<div class="profile-right"')
print('i1,i2', i1, i2)
seg = b[i1:i2+30]
print(repr(seg))
print(seg)
