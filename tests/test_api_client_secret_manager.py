import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import api_client


class TestAPIClientSecretManagerFallback(unittest.TestCase):
    def test_load_api_key_from_secret_map(self):
        # Simulate secret manager returning a map of keys
        fake_secret = 'gems_hub:SECRET1,desktop_app:SECRET2'
        with patch('utils.api_client._get_secret_from_gcp', return_value=fake_secret):
            key = api_client.load_api_key(preferred_app_name='gems_hub')
            self.assertEqual(key, 'SECRET1')

    def test_load_api_key_from_secret_single_value(self):
        fake_secret = 'SINGLE_SECRET'
        with patch('utils.api_client._get_secret_from_gcp', return_value=fake_secret):
            key = api_client.load_api_key(preferred_app_name='gems_hub')
            self.assertEqual(key, 'SINGLE_SECRET')

    def test_env_fallback_when_no_secret_and_no_config(self):
        # Remove env if present
        try:
            del os.environ['GEMDB_API_KEY']
        except KeyError:
            pass
        with patch('utils.api_client._get_secret_from_gcp', return_value=None):
            os.environ['GEMDB_API_KEY'] = 'ENV_SECRET'
            key = api_client.load_api_key(preferred_app_name='gems_hub')
            self.assertEqual(key, 'ENV_SECRET')
            del os.environ['GEMDB_API_KEY']


if __name__ == '__main__':
    unittest.main()
