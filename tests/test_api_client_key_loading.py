import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.api_client import load_api_key


class TestAPIClientKeyLoading(unittest.TestCase):
    def test_load_api_key_from_env(self):
        os.environ['GEMDB_API_KEY'] = 'LOCAL_KEY'
        key = load_api_key()
        self.assertEqual(key, 'LOCAL_KEY')
        del os.environ['GEMDB_API_KEY']


if __name__ == '__main__':
    unittest.main()
