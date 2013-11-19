"""This module contains a collection of unit tests which
validate lib/strutil.py"""

import sys
import os
import unittest

from yar import strutil


class MakeHttpHeaderValueTestCase(unittest.TestCase):

    def test_value_is_none(self):
        v = None
        hv = strutil.make_http_header_value_friendly(v)
        self.assertIsNotNone(hv)
        self.assertEqual(hv, "<None>")

    def test_value_is_not_a_string(self):
        v = 1
        hv = strutil.make_http_header_value_friendly(v)
        self.assertIsNotNone(hv)
        self.assertEqual(hv, str(v))

    def test_value_with_tabs_and_newline(self):
        v = "dave\t\nwas\r"
        hv = strutil.make_http_header_value_friendly(v)
        self.assertIsNotNone(hv)
        self.assertEqual(hv, "dave\\t\\nwas\\r")
