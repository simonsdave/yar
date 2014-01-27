"""This module contains a series of unit tests which
validate lib/mac.py"""

import unittest

from yar.basic import APIKey


class APIKeyTestCase(unittest.TestCase):

    def test_generate_returns_non_none_APIKey(self):
        api_key = APIKey.generate()
        self.assertIsNotNone(api_key)
        self.assertEqual(type(api_key), APIKey)
        self.assertEqual(32, len(api_key))

    def test_created_with_explicit_content(self):
        content = 'dave was here'
        api_key = APIKey(content)
        self.assertIsNotNone(api_key)
        self.assertEqual(api_key, content)
