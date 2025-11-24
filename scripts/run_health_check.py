import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app
from utils.api_client import get_api_key_info

with app.test_client() as client:
    resp = client.get('/health')
    print('status', resp.status_code)
    print(resp.data.decode('utf-8'))
    print('key info', get_api_key_info())
