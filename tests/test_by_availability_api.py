import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestByAvailabilityAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch('routes.gems.get_gems_from_api')
    def test_by_availability_api_populates_gems(self, mock_api):
        # Return a simple API payload for testing
        mock_api.return_value = [
            {
                'gem_type_name': 'Ruby',
                'Availability_Level': 'Collectors Market',
                'Availability_Driver': 'Limited Investment',
                'Availability_Description': 'High-quality trade in auction houses'
            },
            {
                'gem_type_name': 'Rose Quartz',
                'Availability_Level': 'Consistently Available',
                'Availability_Driver': 'Consistent Deposits',
                'Availability_Description': 'Widely available in trade channels'
            }
        ]

        rv = self.client.get('/gems/by-availability')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Ruby', rv.data)
        self.assertIn(b'Rose Quartz', rv.data)

    @patch('routes.gems.get_gems_from_api')
    def test_by_availability_empty_api_returns_no_gems(self, mock_api):
        # API returns empty list -> page should render but have no gems
        mock_api.return_value = []
        rv = self.client.get('/gems/by-availability')
        self.assertEqual(rv.status_code, 200)
        # page should not contain Ruby in this scenario
        self.assertNotIn(b'Ruby', rv.data)


if __name__ == '__main__':
    unittest.main()
