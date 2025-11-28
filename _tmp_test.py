import sys
sys.path.insert(0, r'd:\OneDrive\Documents\GitHub')
from gems import app
app = app.app
app.config.update({'TESTING': True, 'GEMDB_API_URL': 'https://api.preciousstone.info', 'GEMDB_API_KEY': ''})
client = app.test_client()
r = client.get('/gems/gem/diamond')
print('Status:', r.status_code)
body = r.get_data(as_text=True)
print('Len:', len(body))
print('Has listings header:', 'Current Listings' in body)
print('Has table id:', 'id="current-listings"' in body)
print('Has loading text:', 'Loading current listings' in body)
print('Sample table rows:')
from bs4 import BeautifulSoup
try:
	soup = BeautifulSoup(body, 'html.parser')
	t = soup.find('table', id='current-listings')
	if t:
		rows = t.find_all('tr')
		for row in rows[:5]:
			print([c.get_text(strip=True) for c in row.find_all(['td','th'])])
	else:
		print('No table')
except Exception as e:
	print('BS4 not available; show first 500 chars of body')
	print(body[:500])
