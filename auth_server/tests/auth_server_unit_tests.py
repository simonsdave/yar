"""This module contains unit tests for the auth server's auth_server module."""

import logging
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yar_test_util

import auth_server

_logger = logging.getLogger(__name__)


class TestCase(yar_test_util.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass
