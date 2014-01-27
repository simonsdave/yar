"""This module implements the unit tests for the auth server's
async_creds_retriever module used with basic auth scheme."""

import httplib
import json
import os
import sys
import uuid

import mock
import tornado.httpclient
import tornado.httputil

from yar import basic
from yar.auth_server.basic import async_creds_retriever
from yar import key_server
from yar.key_server import jsonschemas
from yar.tests import yar_test_util


class TestAsyncCredsRetriever(yar_test_util.TestCase):

    _key_server = "dave:42"

    @classmethod
    def setUpClass(cls):
        async_creds_retriever.key_server_address = cls._key_server

    @classmethod
    def tearDownClass(cls):
        async_creds_retriever.key_server = None

    def assertKeyServerRequestOk(self, request, api_key):
        self.assertIsNotNone(request)
        self.assertIsNotNone(request.url)
        expected_url = "http://%s/v1.0/creds/%s" % (
            self.__class__._key_server,
            api_key)
        self.assertEqual(request.url, expected_url)
        self.assertIsNotNone(request.method)
        self.assertEqual(request.method, "GET")

    def test_key_server_tornado_error_response(self):
        """Confirm that when the key server returns an error (as
        in a tornado response.error) that this is flagged as an
        error to the callback of the fetch method of
        ```AsyncCredsRetriever```."""
        the_api_key = basic.APIKey.generate()

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_api_key)

            response = mock.Mock()
            response.error = "something"
            response.code = httplib.OK
            callback(response)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):

            def on_async_creds_retriever_done(is_ok, owner=None):
                self.assertIsNotNone(is_ok)
                self.assertFalse(is_ok)

                self.assertIsNone(owner)

            acr = async_creds_retriever.AsyncCredsRetriever(the_api_key)
            acr.fetch(on_async_creds_retriever_done)

    def test_key_server_unexpected_tornado_response_code(self):
        """Confirm that when the key server returns an unexpected
        response code (only expect OK & NOT_FOUND) that this is flagged
        as an error to the callback of the fetch method of
        ```AsyncCredsRetriever```."""
        the_api_key = basic.APIKey.generate()

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_api_key)

            response = mock.Mock()
            response.code = httplib.CREATED
            callback(response)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):

            def on_async_creds_retriever_done(is_ok, owner=None):
                self.assertIsNotNone(is_ok)
                self.assertFalse(is_ok)

                self.assertIsNone(owner)

            acr = async_creds_retriever.AsyncCredsRetriever(the_api_key)
            acr.fetch(on_async_creds_retriever_done)

    def test_creds_not_found(self):
        """Confirm that when the key server returns a NOT_FOUND
        response code that this is flagged as being ok to the callback
        of the fetch method of ```AsyncCredsRetriever```."""
        the_api_key = basic.APIKey.generate()

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_api_key)

            response = mock.Mock()
            response.error = None
            response.code = httplib.NOT_FOUND
            callback(response)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):

            def on_async_creds_retriever_done(is_ok, owner=None):
                self.assertIsNotNone(is_ok)
                self.assertTrue(is_ok)

                self.assertIsNone(owner)

            acr = async_creds_retriever.AsyncCredsRetriever(the_api_key)
            acr.fetch(on_async_creds_retriever_done)

    def test_key_server_returns_zero_length_response(self):
        """Confirm that when the key server returns a zero length
        response this is flagged as an error to the callback the
        fetch method of ```AsyncCredsRetriever```."""
        the_api_key = basic.APIKey.generate()

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_api_key)

            response = mock.Mock()
            response.error = None
            response.code = httplib.OK
            response.headers = tornado.httputil.HTTPHeaders({
                "Content-type": "application/json; charset=utf8",
                "Content-length": "0",
            })
            response.body = ""
            callback(response)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):

            def on_async_creds_retriever_done(is_ok, owner=None):
                self.assertIsNotNone(is_ok)
                self.assertFalse(is_ok)

                self.assertIsNone(owner)

            acr = async_creds_retriever.AsyncCredsRetriever(the_api_key)
            acr.fetch(on_async_creds_retriever_done)

    def test_key_server_returns_body_that_is_not_valid_json(self):
        """Confirm that when the key server returns a response
        body that's not json is flagged as an error to the callback
        the fetch method of ```AsyncCredsRetriever```."""
        the_api_key = basic.APIKey.generate()

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_api_key)

            response = mock.Mock()
            response.error = None
            response.code = httplib.OK
            response.headers = tornado.httputil.HTTPHeaders({
                "Content-type": "application/json; charset=utf8",
                "Content-length": "0",
            })
            response.body = "dave"
            self.assertIsNotJSON(response.body)
            callback(response)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):

            def on_async_creds_retriever_done(is_ok, owner=None):
                self.assertIsNotNone(is_ok)
                self.assertFalse(is_ok)

                self.assertIsNone(owner)

            acr = async_creds_retriever.AsyncCredsRetriever(the_api_key)
            acr.fetch(on_async_creds_retriever_done)

    def test_key_server_returns_body_with_unexpected_json(self):
        """Confirm that when the key server returns a response
        body that's json but has unexpected attributes that this
        is flagged as an error to the callback the fetch method of
        ```AsyncCredsRetriever```."""
        the_api_key = basic.APIKey.generate()

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_api_key)

            response = mock.Mock()
            response.error = None
            response.code = httplib.OK
            response.body = json.dumps({
                "api_key": 24,
            })
            response.headers = tornado.httputil.HTTPHeaders({
                "Content-type": "application/json; charset=utf8",
                "Content-length": str(len(response.body)),
            })
            self.assertIsNotValidJSON(
                response.body,
                key_server.jsonschemas.get_creds_response)
            callback(response)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):

            def on_async_creds_retriever_done(is_ok, owner=None):
                self.assertIsNotNone(is_ok)
                self.assertFalse(is_ok)

                self.assertIsNone(owner)

            acr = async_creds_retriever.AsyncCredsRetriever(the_api_key)
            acr.fetch(on_async_creds_retriever_done)

    def test_all_good(self):
        """This is a happy path test for the fetch method of
        ```AsyncCredsRetriever```."""
        the_api_key = basic.APIKey.generate()
        the_owner = str(uuid.uuid4()).replace("-", "")

        def async_http_client_fetch_patch(http_client, request, callback):
            self.assertKeyServerRequestOk(request, the_api_key)

            response = mock.Mock()
            response.error = None
            response.code = httplib.OK
            response.body = json.dumps({
                "is_deleted": False,
                "basic": {
                    "api_key": the_api_key,
                },
                "owner": the_owner,
                "links": {
                    "self": {
                        "href": "abc",
                    },
                },
            })
            response.headers = tornado.httputil.HTTPHeaders({
                "Content-type": "application/json; charset=utf8",
                "Content-length": str(len(response.body)),
            })
            self.assertIsValidJSON(
                response.body,
                key_server.jsonschemas.get_creds_response)
            callback(response)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):

            def on_async_creds_retriever_done(is_ok, owner=None):
                self.assertIsNotNone(is_ok)
                self.assertTrue(is_ok)

                self.assertIsNotNone(owner)
                self.assertEqual(owner, the_owner)

            acr = async_creds_retriever.AsyncCredsRetriever(the_api_key)
            acr.fetch(on_async_creds_retriever_done)
