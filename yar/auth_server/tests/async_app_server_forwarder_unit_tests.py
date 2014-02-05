"""This module implements the unit tests for the auth server's
async_app_server_forwarder module."""

import httplib
import os
import sys

import mock
import tornado.httputil

from yar.util import mac
from yar.tests import yar_test_util

from yar.auth_server import async_app_server_forwarder

class TestAsyncCredsForwarder(yar_test_util.TestCase):

    _app_server = "dave:42"
    _app_server_auth_method = "BILLYBOB"

    @classmethod
    def setUpClass(cls):
        aasf = async_app_server_forwarder
        aasf.app_server = cls._app_server
        aasf.app_server_auth_method = cls._app_server_auth_method

    @classmethod
    def tearDownClass(cls):
        pass

    def _test_good(
        self,
        the_request_method,
        the_request_uri,
        the_request_headers,
        the_request_body,
        the_response_code,
        the_response_headers,
        the_response_body,
        the_response_content_type):
        """This is a long but very useful utility method that is intended to
        test ```async_app_server_forwarder.AsyncAppServerForwarder```
        forwarding functionality when things are working corectly."""

        the_response_is_ok = True
        the_request_principal = "das@example.com"

        def async_app_server_forwarder_forward_patch(http_client, request, callback):
            self.assertIsNotNone(request)

            expected_url = "http://%s%s" % (
                self.__class__._app_server,
                the_request_uri
            )
            self.assertEqual(request.url, expected_url)

            self.assertIsNotNone(request.method)
            self.assertEqual(request.method, the_request_method)

            self.assertIsNotNone(request.headers)
            self.assertEqual(len(request.headers), 1 + len(the_request_headers))
            expected_headers = tornado.httputil.HTTPHeaders(the_request_headers)
            expected_headers["Authorization"] = "%s %s" % (
                self.__class__._app_server_auth_method,
                the_request_principal)
            self.assertEqual(request.headers, expected_headers)

            response = mock.Mock()
            response.error = None
            response.code = the_response_code
            response.body = the_response_body
            response.headers = tornado.httputil.HTTPHeaders(the_response_headers)
            if response.body:
                response.headers["Content-type"] = the_response_content_type
                response.headers["Content-length"] = str(len(response.body))
            callback(response)

        def on_async_app_server_forward_done(
            is_ok,
            http_status_code,
            headers,
            body):

            self.assertIsNotNone(is_ok)
            self.assertEqual(is_ok, the_response_is_ok)

            if not is_ok:
                return

            self.assertIsNotNone(http_status_code)
            self.assertEqual(http_status_code, the_response_code)

            self.assertIsNotNone(headers)

            if the_response_body is None:
                self.assertIsNone(body)

                self.assertEqual(headers, the_response_headers)
            else:
                self.assertIsNotNone(body)
                self.assertEqual(body, the_response_body)

                self.assertEqual(len(headers), 2 + len(the_response_headers))
                the_expected_headers = tornado.httputil.HTTPHeaders(the_response_headers)
                the_expected_headers["Content-type"] = the_response_content_type
                the_expected_headers["Content-length"] = str(len(body))
                self.assertEqual(headers, the_expected_headers)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_app_server_forwarder_forward_patch):
            aasf = async_app_server_forwarder.AsyncAppServerForwarder(
                the_request_method,
                the_request_uri,
                the_request_headers,
                the_request_body,
                the_request_principal)
            aasf.forward(on_async_app_server_forward_done)

    def test_all_good_001(self):
        """Validate ```async_app_server_forwarder.AsyncAppServerForwarder```
        is working correctly when forwarding requests that have:
            0/ GET
            1/ no request body
            2/ 200 OK response code
            3/ a response body"""
        self._test_good(
            the_request_method = "GET",
            the_request_uri = "/dave.html",
            the_request_headers = {
                "X-Dave-Testing": 42,
            },
            the_request_body = None,
            the_response_code = httplib.OK,
            the_response_headers = tornado.httputil.HTTPHeaders({
                "X-Bindle": "one",
                "X-Berry": "two",
            }),
            the_response_body = "... hello!!!",
            the_response_content_type = "text/plain; charset=utf8")

    def test_all_good_002(self):
        """Validate ```async_app_server_forwarder.AsyncAppServerForwarder```
        is working correctly when forwarding requests that have:
            0/ GET
            1/ no request body
            2/ 404 not found response code
            3/ no response body"""
        self._test_good(
            the_request_method = "GET",
            the_request_uri = "/dave.html",
            the_request_headers = {
                "X-Dave-Testing": 42,
            },
            the_request_body = None,
            the_response_code = httplib.NOT_FOUND,
            the_response_headers = tornado.httputil.HTTPHeaders({
                "X-Bindle": "one",
                "X-Berry": "two",
            }),
            the_response_body = None,
            the_response_content_type = None)

    def test_all_good_003(self):
        """Validate ```async_app_server_forwarder.AsyncAppServerForwarder```
        is working correctly when forwarding requests that have:
            0/ GET
            1/ no request body
            2/ 200 ok response code
            3/ no response body"""
        self._test_good(
            the_request_method = "GET",
            the_request_uri = "/dave.html",
            the_request_headers = {
                "X-Dave-Testing": 42,
            },
            the_request_body = None,
            the_response_code = httplib.OK,
            the_response_headers = tornado.httputil.HTTPHeaders({
                "X-Bindle": "one",
                "X-Berry": "two",
            }),
            the_response_body = None,
            the_response_content_type = None)

    def test_all_good_004(self):
        """Validate ```async_app_server_forwarder.AsyncAppServerForwarder```
        is working correctly when forwarding POST requests that have:
            0/ POST
            1/ no request body
            2/ 201 created response code
            3/ no response body"""
        self._test_good(
            the_request_method = "POST",
            the_request_uri = "/mvs/",
            the_request_headers = {
                "X-Dave-Testing": 42,
                "Content-type": "text/plain; charset=utf8",
            },
            the_request_body = "dave was here",
            the_response_code = httplib.CREATED,
            the_response_headers = tornado.httputil.HTTPHeaders({
                "X-Bindle": "one",
                "X-Berry": "two",
            }),
            the_response_body = None,
            the_response_content_type = None)

    def test_error(self):
        """This is a long but very useful utility method that is intended to
        test ```async_app_server_forwarder.AsyncAppServerForwarder```
        forwarding functionality when things are working corectly."""
        the_request_method = "GET"
        the_request_uri = "/mvs/"
        the_request_headers = {
            "X-Dave-Testing": 42,
        }
        the_request_body = "dave was here"
        the_request_principal = "das@example.com"

        the_response_code = httplib.CREATED
        the_response_headers = tornado.httputil.HTTPHeaders({
            "X-Bindle": "one",
            "X-Berry": "two",
        })
        the_response_body = None
        the_response_content_type = None

        the_response_is_ok = True

        def async_app_server_forwarder_forward_patch(http_client, request, callback):
            self.assertIsNotNone(request)

            expected_url = "http://%s%s" % (
                self.__class__._app_server,
                the_request_uri
            )
            self.assertEqual(request.url, expected_url)

            self.assertIsNotNone(request.method)
            self.assertEqual(request.method, the_request_method)

            self.assertIsNotNone(request.headers)
            self.assertEqual(len(request.headers), 1 + len(the_request_headers))
            expected_headers = tornado.httputil.HTTPHeaders(the_request_headers)
            expected_headers["Authorization"] = "%s %s" % (
                self.__class__._app_server_auth_method,
                the_request_principal)
            self.assertEqual(request.headers, expected_headers)

            response = mock.Mock()
            response.error = "something"
            response.code = httplib.NOT_FOUND
            callback(response)

        def on_async_app_server_forward_done(is_ok):
            self.assertIsNotNone(is_ok)
            self.assertFalse(is_ok)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_app_server_forwarder_forward_patch):
            aasf = async_app_server_forwarder.AsyncAppServerForwarder(
                the_request_method,
                the_request_uri,
                the_request_headers,
                the_request_body,
                the_request_principal)
            aasf.forward(on_async_app_server_forward_done)
