"""This module implements the unit tests for the auth service's
async_mac_creds_retriever module."""

import httplib
import json
import os
import sys

import mock
import tornado.httpclient
import tornado.httputil

from yar.auth_service.mac import async_mac_creds_retriever
from yar import key_service
from yar.key_service import jsonschemas
from yar.util import mac
from yar.tests import yar_test_util


class TestAsyncMACCredsRetriever(yar_test_util.TestCase):

    _key_service = "dave:42"

    @classmethod
    def setUpClass(cls):
        async_mac_creds_retriever.key_service_address = cls._key_service

    @classmethod
    def tearDownClass(cls):
        async_mac_creds_retriever.key_service = None

    def assertKeyServerRequestOk(self, request, mac_key_identifier):
        self.assertIsNotNone(request)
        self.assertIsNotNone(request.url)
        expected_url = "http://%s/v1.0/creds/%s" % (
            self.__class__._key_service,
            mac_key_identifier)
        self.assertEqual(request.url, expected_url)
        self.assertIsNotNone(request.method)
        self.assertEqual(request.method, "GET")

    def test_key_service_tornado_error_response(self):
        """Confirm that when the key service returns an error (as
        in a tornado response.error) that this is flagged as an
        error to the callback of the fetch method of
        ```AsyncMACCredsRetriever```."""
        the_mac_key_identifier = mac.MACKeyIdentifier.generate()

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_mac_key_identifier)

            response = mock.Mock()
            response.error = "something"
            response.request_time = 24
            callback(response)

        def on_async_mac_creds_retriever_done(is_ok, mac_key_identifier):
            self.assertIsNotNone(is_ok)
            self.assertFalse(is_ok)
            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            acr = async_mac_creds_retriever.AsyncMACCredsRetriever(the_mac_key_identifier)
            acr.fetch(on_async_mac_creds_retriever_done)

    def test_key_service_tornado_http_error_response(self):
        """Confirm that when the key service returns an http error (as
        a non httplib.ok response.code) that this is flagged as an
        error to the callback of the fetch method of
        ```AsyncMACCredsRetriever```."""
        the_mac_key_identifier = mac.MACKeyIdentifier.generate()

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_mac_key_identifier)

            response = mock.Mock()
            response.error = None
            response.code = httplib.NOT_FOUND
            response.request_time = 24
            callback(response)

        def on_async_mac_creds_retriever_done(is_ok, mac_key_identifier):
            self.assertIsNotNone(is_ok)
            self.assertFalse(is_ok)
            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            acr = async_mac_creds_retriever.AsyncMACCredsRetriever(the_mac_key_identifier)
            acr.fetch(on_async_mac_creds_retriever_done)

    def test_key_service_returns_zero_length_response(self):
        """Confirm that when the key service returns a zero length
        response this is flagged as an error to the callback the
        fetch method of ```AsyncMACCredsRetriever```."""
        the_mac_key_identifier = mac.MACKeyIdentifier.generate()

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_mac_key_identifier)

            response = mock.Mock()
            response.error = None
            response.code = httplib.OK
            response.headers = tornado.httputil.HTTPHeaders({
                "Content-type": "application/json; charset=utf8",
                "Content-length": "0",
            })
            response.body = ""
            response.request_time = 24
            callback(response)

        def on_async_mac_creds_retriever_done(is_ok, mac_key_identifier):
            self.assertIsNotNone(is_ok)
            self.assertFalse(is_ok)
            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            acr = async_mac_creds_retriever.AsyncMACCredsRetriever(the_mac_key_identifier)
            acr.fetch(on_async_mac_creds_retriever_done)

    def test_key_service_returns_non_json_response(self):
        """Confirm that when the key service returns a non-zero length
        response that is not JSON this is flagged as an error to the callback
        the fetch method of ```AsyncMACCredsRetriever```."""
        the_mac_key_identifier = mac.MACKeyIdentifier.generate()

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_mac_key_identifier)

            response = mock.Mock()
            response.error = None
            response.code = httplib.OK
            response.body = "dave"
            self.assertIsNotJSON(response.body)
            response.headers = tornado.httputil.HTTPHeaders({
                "Content-type": "application/json; charset=utf8",
                "Content-length": str(len(response.body)),
            })
            response.request_time = 24
            callback(response)

        def on_async_mac_creds_retriever_done(is_ok, mac_key_identifier):
            self.assertIsNotNone(is_ok)
            self.assertFalse(is_ok)
            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            acr = async_mac_creds_retriever.AsyncMACCredsRetriever(the_mac_key_identifier)
            acr.fetch(on_async_mac_creds_retriever_done)

    def test_key_service_returns_an_invalid_json_response(self):
        """Confirm that when the key service returns a valid JSON document
        but the JSON contains unexpected properties is flagged as an error
        to the callback the fetch method of ```AsyncMACCredsRetriever```."""
        the_mac_key_identifier = mac.MACKeyIdentifier.generate()

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_mac_key_identifier)

            response = mock.Mock()
            response.error = None
            response.code = httplib.OK
            response.body = json.dumps({
                "is_deleted": False,
                "mac_key": "01234",
            })
            self.assertIsNotValidJSON(
                response.body,
                key_service.jsonschemas.get_creds_response)
            response.headers = tornado.httputil.HTTPHeaders({
                "Content-type": "application/json; charset=utf8",
                "Content-length": str(len(response.body)),
            })
            response.request_time = 24
            callback(response)

        def on_async_mac_creds_retriever_done(is_ok, mac_key_identifier):
            self.assertIsNotNone(is_ok)
            self.assertFalse(is_ok)
            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            acr = async_mac_creds_retriever.AsyncMACCredsRetriever(the_mac_key_identifier)
            acr.fetch(on_async_mac_creds_retriever_done)

    def test_key_service_returns_all_good(self):
        """Confirm that when the key service returns a valid JSON document
        but the JSON contains unexpected properties is flagged as an error
        to the callback the fetch method of ```AsyncMACCredsRetriever```."""
        the_mac_key_identifier = mac.MACKeyIdentifier.generate()
        the_mac_algorithm = "hmac-sha-1"
        the_mac_key = mac.MACKey.generate()
        the_principal = "das@example.com"

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_mac_key_identifier)

            response = mock.Mock()
            response.error = None
            response.code = httplib.OK
            response.body = json.dumps({
                "mac": {
                    "mac_algorithm": the_mac_algorithm,
                    "mac_key": the_mac_key,
                    "mac_key_identifier": the_mac_key_identifier,
                },
                "principal": the_principal,
                "links": {
                    "self": {
                        "href": "abc",
                    }
                }
            })
            self.assertIsValidJSON(
                response.body,
                key_service.jsonschemas.get_creds_response)
            response.headers = tornado.httputil.HTTPHeaders({
                "Content-type": "application/json; charset=utf8",
                "Content-length": str(len(response.body)),
            })
            response.request_time = 24
            callback(response)

        def on_async_mac_creds_retriever_done(is_ok,
                                              mac_key_identifier,
                                              mac_algorithm,
                                              mac_key,
                                              principal):

            self.assertIsNotNone(is_ok)
            self.assertTrue(is_ok)

            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)

            self.assertIsNotNone(mac_algorithm)
            self.assertEqual(mac_algorithm, the_mac_algorithm)

            self.assertIsNotNone(mac_key)
            self.assertEqual(mac_key, the_mac_key)

            self.assertIsNotNone(principal)
            self.assertEqual(principal, the_principal)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            acr = async_mac_creds_retriever.AsyncMACCredsRetriever(the_mac_key_identifier)
            acr.fetch(on_async_mac_creds_retriever_done)
