import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestByInvestmentAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch('routes.gems.get_gems_from_api')
    def test_by_investment_api_populates_gems(self, mock_api):
        mock_api.return_value = [
            {
                'gem_type_name': 'Ruby',
                'Investment_Appropriateness_Level': 'Blue Chip Investment Gems',
                'Investment_Appropriateness_Description': 'High investment potential'
            },
            {
                'gem_type_name': 'Rose Quartz',
                'Investment_Appropriateness_Level': 'Non-Investment Gems',
                'Investment_Appropriateness_Description': 'Decorative only'
            }
        ]

        rv = self.client.get('/gems/by-investment')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Ruby', rv.data)
        self.assertIn(b'Rose Quartz', rv.data)

    @patch('routes.gems.get_gems_from_api')
    def test_by_investment_empty_api_fallback_yaml(self, mock_api):
        # API returns empty list; page should still render using YAML fallback
        mock_api.return_value = []
        rv = self.client.get('/gems/by-investment')
        self.assertEqual(rv.status_code, 200)
        # Expect 'Ruby' to be present from YAML fallback
        self.assertIn(b'Ruby', rv.data)


if __name__ == '__main__':
    unittest.main()
