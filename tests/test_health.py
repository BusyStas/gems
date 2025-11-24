import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class TestHealthEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch('routes.main.get_api_health')
    @patch('routes.main.get_api_key_info')
    def test_health_shows_api_and_key_status(self, mock_get_key_info, mock_get_health):
        mock_get_health.return_value = {'status_code': 200, 'body': {'status': 'ok'}}
        # key shorter than 100 chars
        mock_get_key_info.return_value = ('SHORT_KEY', 'env')
        rv = self.client.get('/health')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'API Health', rv.data)
        self.assertIn(b'No', rv.data)  # key is not >100 chars

    @patch('routes.main.get_api_health')
    @patch('routes.main.get_api_key_info')
    def test_health_key_long(self, mock_get_key_info, mock_get_health):
        mock_get_health.return_value = {'status_code': 200, 'body': {'status': 'ok'}}
        mock_get_key_info.return_value = ('X' * 200, 'env')
        rv = self.client.get('/health')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Yes', rv.data)  # key > 100 chars

    @patch('routes.main.get_api_health')
    @patch('routes.main.get_api_key_info')
    def test_health_api_unavailable(self, mock_get_key_info, mock_get_health):
        mock_get_health.return_value = None
        mock_get_key_info.return_value = (None, None)
        rv = self.client.get('/health')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Unavailable', rv.data)

if __name__ == '__main__':
    unittest.main()
