"""This module contains a series of unit tests which
validate yar.util.mac.RequestsAuth's functionality."""

import json
import unittest

import mock
import requests

from yar.util import mac


class TestRequestsAuth(unittest.TestCase):
    """These unit tests verify the behavior of
    yar.util.mac.RequestsAuth"""

    def test_all_good_http_get_with_port(self):
        """Verify the behavior of yar.util.mac.RequestsAuth
        for HTTP GETs where the URL contains a port."""

        mac_key_identifier = mac.MACKeyIdentifier.generate()
        mac_key = mac.MACKey.generate()
        mac_algorithm = mac.MAC.algorithm

        auth = mac.RequestsAuth(
            mac_key_identifier,
            mac_key,
            mac_algorithm)

        mock_request = mock.Mock()
        mock_request.headers = {}
        mock_request.body = None
        mock_request.method = "GET"
        mock_request.url = "http://localhost:8000"

        rv = auth(mock_request)

        self.assertIsNotNone(rv)
        self.assertIs(rv, mock_request)
        self.assertTrue("Authorization" in mock_request.headers)
        ahv = mac.AuthHeaderValue.parse(mock_request.headers["Authorization"])
        self.assertIsNotNone(ahv)
        self.assertEqual(ahv.mac_key_identifier, mac_key_identifier)
        self.assertEqual(ahv.ext, "")

    def test_all_good_http_get_without_port(self):
        """Verify the behavior of yar.util.mac.RequestsAuth
        for HTTP GETs where the URL contains no port."""

        mac_key_identifier = mac.MACKeyIdentifier.generate()
        mac_key = mac.MACKey.generate()
        mac_algorithm = mac.MAC.algorithm

        auth = mac.RequestsAuth(
            mac_key_identifier,
            mac_key,
            mac_algorithm)

        mock_request = mock.Mock()
        mock_request.headers = {}
        mock_request.body = None
        mock_request.method = "GET"
        mock_request.url = "http://localhost"

        rv = auth(mock_request)

        self.assertIsNotNone(rv)
        self.assertIs(rv, mock_request)
        self.assertTrue("Authorization" in mock_request.headers)
        ahv = mac.AuthHeaderValue.parse(mock_request.headers["Authorization"])
        self.assertIsNotNone(ahv)
        self.assertEqual(ahv.mac_key_identifier, mac_key_identifier)
        self.assertEqual(ahv.ext, "")

    def test_all_good_http_post(self):
        """Verify the behavior of yar.util.mac.RequestsAuth
        for HTTP POSTs."""

        mac_key_identifier = mac.MACKeyIdentifier.generate()
        mac_key = mac.MACKey.generate()
        mac_algorithm = mac.MAC.algorithm

        auth = mac.RequestsAuth(
            mac_key_identifier,
            mac_key,
            mac_algorithm)

        mock_request = mock.Mock()
        mock_request.headers = {
            "content-type": "application/json",
        }
        body = {
            1: 2,
            3: 4,
        }
        mock_request.body = json.dumps(body)
        mock_request.method = "POST"
        mock_request.url = "http://localhost:8000"

        rv = auth(mock_request)

        self.assertIsNotNone(rv)
        self.assertIs(rv, mock_request)
        self.assertTrue("Authorization" in mock_request.headers)
        ahv = mac.AuthHeaderValue.parse(mock_request.headers["Authorization"])
        self.assertIsNotNone(ahv)
        self.assertEqual(ahv.mac_key_identifier, mac_key_identifier)
        self.assertNotEqual(ahv.ext, "")
