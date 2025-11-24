import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestGemProfile(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_gem_profile_underscore_slug(self):
        rv = self.client.get('/gems/gem/rose_quartz')
        self.assertEqual(rv.status_code, 200)
        # page contains header with gem name
        self.assertIn(b'Rose Quartz', rv.data)

    def test_gem_profile_hyphen_slug(self):
        rv = self.client.get('/gems/gem/rose-quartz')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Rose Quartz', rv.data)


if __name__ == '__main__':
    unittest.main()
