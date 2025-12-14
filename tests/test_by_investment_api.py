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
        # Mock API returns PascalCase field names (v2 API format)
        mock_api.return_value = [
            {
                'GemTypeName': 'Ruby',
                'InvestmentAppropriatenessLevel': 'Blue Chip Investment Gems',
                'InvestmentAppropriatenessDescription': 'High investment potential'
            },
            {
                'GemTypeName': 'Rose Quartz',
                'InvestmentAppropriatenessLevel': 'Non-Investment Gems',
                'InvestmentAppropriatenessDescription': 'Decorative only'
            }
        ]

        rv = self.client.get('/gems/by-investment')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Ruby', rv.data)
        self.assertIn(b'Rose Quartz', rv.data)

    @patch('routes.gems.get_gems_from_api')
    def test_by_investment_empty_api_returns_empty(self, mock_api):
        # API returns empty list; page should still render but with no gems
        mock_api.return_value = []
        rv = self.client.get('/gems/by-investment')
        self.assertEqual(rv.status_code, 200)
        # Page should render successfully with the title
        self.assertIn(b'Investment Appropriateness', rv.data)


if __name__ == '__main__':
    unittest.main()
