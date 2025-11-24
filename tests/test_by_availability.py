import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestByAvailability(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch('routes.gems.get_gems_from_api')
    def test_by_availability_page_has_gems(self, mock_api):
        mock_api.return_value = [
            {
                'gem_type_name': 'Ruby',
                'Availability_Level': 'Collectors Market',
                'Availability_Driver': 'Limited Investment',
                'Availability_Description': 'High-quality trade in auction houses'
            }
        ]
        rv = self.client.get('/gems/by-availability')
        self.assertEqual(rv.status_code, 200)
        # Check that the page contains a known gem name provided by API
        self.assertIn(b'Ruby', rv.data)


if __name__ == '__main__':
    unittest.main()
