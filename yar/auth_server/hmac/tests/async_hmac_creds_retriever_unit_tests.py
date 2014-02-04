"""This module implements the unit tests for the auth server's
async_hmac_creds_retriever module."""

import httplib
import json
import os
import sys

import mock
import tornado.httpclient
import tornado.httputil

from yar.auth_server.hmac import async_hmac_creds_retriever
from yar import key_server
from yar.key_server import jsonschemas
from yar import mac
from yar.tests import yar_test_util


class TestAsyncHMACCredsRetriever(yar_test_util.TestCase):

    _key_server = "dave:42"

    @classmethod
    def setUpClass(cls):
        async_hmac_creds_retriever.key_server_address = cls._key_server

    @classmethod
    def tearDownClass(cls):
        async_hmac_creds_retriever.key_server = None

    def assertKeyServerRequestOk(self, request, mac_key_identifier):
        self.assertIsNotNone(request)
        self.assertIsNotNone(request.url)
        expected_url = "http://%s/v1.0/creds/%s" % (
            self.__class__._key_server,
            mac_key_identifier)
        self.assertEqual(request.url, expected_url)
        self.assertIsNotNone(request.method)
        self.assertEqual(request.method, "GET")

    def test_key_server_tornado_error_response(self):
        """Confirm that when the key server returns an error (as
        in a tornado response.error) that this is flagged as an
        error to the callback of the fetch method of
        ```AsyncHMACCredsRetriever```."""
        the_mac_key_identifier = mac.MACKeyIdentifier.generate()

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_mac_key_identifier)

            response = mock.Mock()
            response.error = "something"
            callback(response)

        def on_async_hmac_creds_retriever_done(is_ok, mac_key_identifier):
            self.assertIsNotNone(is_ok)
            self.assertFalse(is_ok)
            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            acr = async_hmac_creds_retriever.AsyncHMACCredsRetriever(the_mac_key_identifier)
            acr.fetch(on_async_hmac_creds_retriever_done)

    def test_key_server_tornado_http_error_response(self):
        """Confirm that when the key server returns an http error (as
        a non httplib.ok response.code) that this is flagged as an
        error to the callback of the fetch method of
        ```AsyncHMACCredsRetriever```."""
        the_mac_key_identifier = mac.MACKeyIdentifier.generate()

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_mac_key_identifier)

            response = mock.Mock()
            response.error = None
            response.code = httplib.NOT_FOUND
            callback(response)

        def on_async_hmac_creds_retriever_done(is_ok, mac_key_identifier):
            self.assertIsNotNone(is_ok)
            self.assertFalse(is_ok)
            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            acr = async_hmac_creds_retriever.AsyncHMACCredsRetriever(the_mac_key_identifier)
            acr.fetch(on_async_hmac_creds_retriever_done)

    def test_key_server_returns_zero_length_response(self):
        """Confirm that when the key server returns a zero length
        response this is flagged as an error to the callback the
        fetch method of ```AsyncHMACCredsRetriever```."""
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
            callback(response)

        def on_async_hmac_creds_retriever_done(is_ok, mac_key_identifier):
            self.assertIsNotNone(is_ok)
            self.assertFalse(is_ok)
            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            acr = async_hmac_creds_retriever.AsyncHMACCredsRetriever(the_mac_key_identifier)
            acr.fetch(on_async_hmac_creds_retriever_done)

    def test_key_server_returns_non_json_response(self):
        """Confirm that when the key server returns a non-zero length
        response that is not JSON this is flagged as an error to the callback
        the fetch method of ```AsyncHMACCredsRetriever```."""
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
            callback(response)

        def on_async_hmac_creds_retriever_done(is_ok, mac_key_identifier):
            self.assertIsNotNone(is_ok)
            self.assertFalse(is_ok)
            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            acr = async_hmac_creds_retriever.AsyncHMACCredsRetriever(the_mac_key_identifier)
            acr.fetch(on_async_hmac_creds_retriever_done)

    def test_key_server_returns_an_invalid_json_response(self):
        """Confirm that when the key server returns a valid JSON document
        but the JSON contains unexpected properties is flagged as an error
        to the callback the fetch method of ```AsyncHMACCredsRetriever```."""
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
                key_server.jsonschemas.get_creds_response)
            response.headers = tornado.httputil.HTTPHeaders({
                "Content-type": "application/json; charset=utf8",
                "Content-length": str(len(response.body)),
            })
            callback(response)

        def on_async_hmac_creds_retriever_done(is_ok, mac_key_identifier):
            self.assertIsNotNone(is_ok)
            self.assertFalse(is_ok)
            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            acr = async_hmac_creds_retriever.AsyncHMACCredsRetriever(the_mac_key_identifier)
            acr.fetch(on_async_hmac_creds_retriever_done)

    def test_key_server_returns_all_good(self):
        """Confirm that when the key server returns a valid JSON document
        but the JSON contains unexpected properties is flagged as an error
        to the callback the fetch method of ```AsyncHMACCredsRetriever```."""
        the_mac_key_identifier = mac.MACKeyIdentifier.generate()
        the_is_deleted = False
        the_mac_algorithm = "hmac-sha-1"
        the_mac_key = mac.MACKey.generate()
        the_principal = "das@example.com"

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_mac_key_identifier)

            response = mock.Mock()
            response.error = None
            response.code = httplib.OK
            response.body = json.dumps({
                "hmac": {
                    "mac_algorithm": the_mac_algorithm,
                    "mac_key": the_mac_key,
                    "mac_key_identifier": the_mac_key_identifier,
                },
                "is_deleted": the_is_deleted,
                "principal": the_principal,
                "links": {
                    "self": {
                        "href": "abc",
                    }
                }
            })
            self.assertIsValidJSON(
                response.body,
                key_server.jsonschemas.get_creds_response)
            response.headers = tornado.httputil.HTTPHeaders({
                "Content-type": "application/json; charset=utf8",
                "Content-length": str(len(response.body)),
            })
            callback(response)

        def on_async_hmac_creds_retriever_done(
            is_ok,
            mac_key_identifier,
            is_deleted,
            mac_algorithm,
            mac_key,
            principal):

            self.assertIsNotNone(is_ok)
            self.assertTrue(is_ok)

            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)

            self.assertIsNotNone(is_deleted)
            self.assertEqual(is_deleted, the_is_deleted)

            self.assertIsNotNone(mac_algorithm)
            self.assertEqual(mac_algorithm, the_mac_algorithm)

            self.assertIsNotNone(mac_key)
            self.assertEqual(mac_key, the_mac_key)

            self.assertIsNotNone(principal)
            self.assertEqual(principal, the_principal)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            acr = async_hmac_creds_retriever.AsyncHMACCredsRetriever(the_mac_key_identifier)
            acr.fetch(on_async_hmac_creds_retriever_done)
