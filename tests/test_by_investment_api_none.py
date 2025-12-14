import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestByInvestmentAPINone(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch('routes.gems.get_gems_from_api')
    def test_by_investment_api_none_returns_empty(self, mock_api):
        # Simulate a call that returns None (e.g., 401). The route should return empty data.
        mock_api.return_value = None
        rv = self.client.get('/gems/by-investment')
        self.assertEqual(rv.status_code, 200)
        # Route should still render successfully but with no gems listed
        self.assertIn(b'Investment Appropriateness', rv.data)


if __name__ == '__main__':
    unittest.main()
