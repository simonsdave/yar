"""This module contains unit tests for the auth server's
auth_server_request_handler module."""

import httplib
import os
import sys
import unittest
import uuid

import httplib2
import mock
import tornado.httpserver
import tornado.httputil
import tornado.web
import tornado.testing

from yar.tests import yar_test_util
from yar.auth_server import auth_server_request_handler


class AuthServer(yar_test_util.Server):
    """Mock auth server."""

    def __init__(self):
        """Creates an instance of the auth server and starts the
        server listenting on a random, available port."""
        yar_test_util.Server.__init__(self)

        handlers = [
            (
                auth_server_request_handler.url_spec,
                auth_server_request_handler.RequestHandler
            ),
        ]
        app = tornado.web.Application(handlers=handlers)
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.add_sockets([self.socket])


class DebugHeadersDict(dict):

    lc_debug_header_prefix = \
        auth_server_request_handler.debug_header_prefix.lower()

    lc_auth_failure_detail_header_name = \
        auth_server_request_handler.auth_failure_detail_header_name.lower()

    def __init__(self, response):
        dict.__init__(self)

        self.auth_failure_detail = None

        len_lc_debug_header_prefix = len(type(self).lc_debug_header_prefix)
        for key, value in response.iteritems():
            if self._is_auth_failure_detail_header_key(key):
                self.auth_failure_detail = value
            else:
                if self._is_debug_header_key(key):
                    self[key[len_lc_debug_header_prefix:]] = value 

    def _is_debug_header_key(self, key):
        lc_key = key.lower()
        if not lc_key.startswith(type(self).lc_debug_header_prefix):
            return False
        if self._is_auth_failure_detail_header_key(key):
            return False
        return True

    def _is_auth_failure_detail_header_key(self, key):
        return type(self).lc_auth_failure_detail_header_name == key.lower()

    def is_equal(self, debug_headers):
        if debug_headers is None:
            return False
        lc_self = {k.lower(): v for k, v in self.iteritems()}
        lc_debug_headers = {k.lower(): v for k, v in debug_headers.iteritems()}
        return lc_self == lc_debug_headers


class MyTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        handlers = [
            (
                auth_server_request_handler.url_spec,
                auth_server_request_handler.RequestHandler
            ),
        ]
        self.app = tornado.web.Application(handlers=handlers)
        return self.app

    @classmethod
    def setUpClass(cls):
        auth_server_request_handler._include_auth_failure_debug_details = True

    @classmethod
    def tearDownClass(cls):
        auth_server_request_handler._include_auth_failure_debug_details = False

    def _assertAuthorizationFailureDetail(self, response, auth_failure_detail):
        """Assert an authorization failure detail HTTP header appears
        in ```response``` with a value equal to ```auth_failure_detail```."""
        for key, value in response.headers.iteritems():
            if auth_server_request_handler.auth_failure_detail_header_name.lower() == key.lower():
                self.assertEqual(int(value), auth_failure_detail)
                return

        self.assertTrue(False)

    def test_no_authorization_header(self):
        """This test confirms that authentication fails if no Authorization
        header is supplied in the auth server's."""
        response = self.fetch("/", method="GET", headers={})
        self.assertEqual(response.code, httplib.UNAUTHORIZED)
        self._assertAuthorizationFailureDetail(
            response,
            auth_server_request_handler.AUTH_FAILURE_DETAIL_NO_AUTH_HEADER)

    def test_invalid_authorization_header(self):
        """This test confirms that authentication fails if an Authorization
        header is supplied but it contains an unrecognized authententication
        scheme."""
        response = self.fetch("/", method="GET", headers={"Authorization": "DAVE"})
        self.assertEqual(response.code, httplib.UNAUTHORIZED)
        self._assertAuthorizationFailureDetail(
            response,
            auth_server_request_handler.AUTH_FAILURE_DETAIL_UNKNOWN_AUTHENTICATION_SCHEME)

    def test_hmac_auth_failed_auth_failure_detail_in_auth_server_response(self):
        """This test confirms that when an authenticator
        supplies authentication failure detail that the failure
        detail is in the auth server's HTTP response as an HTTP header."""

        the_auth_failure_detail = auth_server_request_handler.AUTH_FAILURE_DETAIL_FOR_TESTING

        def authenticate_patch(authenticator, callback):
            callback(is_auth_ok=False, auth_failure_detail=the_auth_failure_detail)

        name_of_method_to_patch = (
            "yar.auth_server.hmac."
            "async_hmac_auth.AsyncHMACAuth.authenticate"
        )
        with mock.patch(name_of_method_to_patch, authenticate_patch):
            response = self.fetch("/", method="GET", headers={"Authorization": "MAC ..."})
            self.assertEqual(response.code, httplib.UNAUTHORIZED)
            self._assertAuthorizationFailureDetail(response, the_auth_failure_detail)


class TestCase(yar_test_util.TestCase):
    """```TestCase``` contains all the unit tests for the
    ```auth_server``` module of the authentication server."""

    @classmethod
    def setUpClass(cls):
        cls.io_loop = yar_test_util.IOLoop()
        cls.io_loop.start()
        cls.auth_server = AuthServer()

    @classmethod
    def tearDownClass(cls):
        # :TODO: is this shutdown sequence right? shouldn't it be the
        # reverse of the startup sequence?
        cls.io_loop.stop()
        cls.io_loop = None
        cls.auth_server.shutdown()
        cls.auth_server = None

    def assertAuthorizationFailureDetail(
        self,
        response,
        auth_failure_detail=None):
        """If ```auth_failure_detail``` is None, assert an
        authorization failure detail HTTP header does not appear in
        ```response```. If ```auth_failure_detail``` is not None
        then assert an authorization failure detail HTTP header appears
        in ```response``` with a value equal to ```auth_failure_detail```."""
        self.assertIsNotNone(response)
        debug_headers_in_response = DebugHeadersDict(response)
        auth_failure_detail_header_value = debug_headers_in_response.auth_failure_detail
        if auth_failure_detail is None:
            self.assertIsNone(auth_failure_detail_header_value)
        else:
            self.assertIsNotNone(auth_failure_detail_header_value)
            self.assertEqual(
                auth_failure_detail_header_value,
                auth_failure_detail)

    def assertAuthorizationDebugHeaders(self, response, debug_headers=None):
        """If ```debug_headers``` is None, assert that no
        authorization failure debug HTTP headers appear in
        ```response```. If ```debug_headers``` is not None
        then assert all of these authorization failure debug HTTP headers
        and only these debug headers appear in ```response```."""
        self.assertIsNotNone(response)
        debug_headers_in_response = DebugHeadersDict(response)
        if debug_headers is None:
            self.assertTrue(0 == len(debug_headers_in_response))
        else:
            self.assertTrue(debug_headers_in_response.is_equal(debug_headers))

    def test_hmac_auth_failed(self):
        """Verify that when async authentication fails, the response
        is ```httplib.UNAUTHORIZED```.

        This test will also confirm that when the authenication
        mechanism fails to supply authentication failure detail,
        no authentication failure detail HTTP header is included
        in the response.

        Fianlly, this tests verifies that an authenication failure
        which generates no debug headers results in an HTTP response
        from the auth server with no debug headers."""
        def authenticate_patch(an_async_hmac_auth, callback):
            self.assertIsNotNone(an_async_hmac_auth)
            self.assertIsNotNone(callback)
            callback(is_auth_ok=False)

        name_of_method_to_patch = (
            "yar.auth_server.hmac."
            "async_hmac_auth.AsyncHMACAuth.authenticate"
        )
        with mock.patch(name_of_method_to_patch, authenticate_patch):
            def forward_patch(ignore_async_app_server_forwarder, callback):
                """This should never be called when authentication fails."""
                self.assertTrue(False)

            name_of_method_to_patch = (
                "yar.auth_server."
                "async_app_server_forwarder.AsyncAppServerForwarder.forward"
            )
            with mock.patch(name_of_method_to_patch, forward_patch):
                http_client = httplib2.Http()
                response, content = http_client.request(
                    "http://localhost:%d/whatever" % type(self).auth_server.port,
                    "GET",
                    headers={"Authorization": "MAC ..."})
                self.assertIsNotNone(response)
                self.assertIsNotNone(response.status)
                self.assertEqual(response.status, httplib.UNAUTHORIZED)
                self.assertAuthorizationFailureDetail(response)
                self.assertAuthorizationDebugHeaders(response)

    @unittest.skip("only for a wee bit")
    def test_auth_failure_debug_details_in_auth_server_response(self):
        """This test confirms that when the authenication
        mechanism supplies debug headers
        that the debug headers are the auth server's HTTP response."""

        prefix = auth_server_request_handler.debug_header_prefix.lower()
        the_auth_failure_debug_details = {
            str(uuid.uuid4()).replace("-", ""): str(uuid.uuid4()).replace("-", ""),
            str(uuid.uuid4()).replace("-", ""): str(uuid.uuid4()).replace("-", ""),
            str(uuid.uuid4()).replace("-", ""): str(uuid.uuid4()).replace("-", ""),
        }

        def authenticate_patch(an_async_hmac_auth, callback):
            self.assertIsNotNone(an_async_hmac_auth)
            self.assertIsNotNone(callback)
            callback(
                is_auth_ok=False,
                auth_failure_debug_details=the_auth_failure_debug_details)

        name_of_method_to_patch = (
            "yar.auth_server.hmac."
            "async_hmac_auth.AsyncHMACAuth.authenticate"
        )
        with mock.patch(name_of_method_to_patch, authenticate_patch):
            def forward_patch(ignore_async_app_server_forwarder, callback):
                """This should never be called when authentication fails."""
                self.assertTrue(False)

            name_of_method_to_patch = (
                "yar.auth_server."
                "async_app_server_forwarder.AsyncAppServerForwarder.forward"
            )
            with mock.patch(name_of_method_to_patch, forward_patch):
                http_client = httplib2.Http()
                response, content = http_client.request(
                    "http://localhost:%d/whatever" % type(self).auth_server.port,
                    "GET",
                    headers={"Authorization": "MAC ..."})
                self.assertIsNotNone(response)
                self.assertIsNotNone(response.status)
                self.assertEqual(response.status, httplib.UNAUTHORIZED)
                self.assertAuthorizationFailureDetail(response)
                self.assertAuthorizationDebugHeaders(
                    response,
                    the_auth_failure_debug_details)

    def test_forward_to_app_server_failed(self):
        """Verify that when async the foward to the app server fails,
        that the response is ```httplib.INTERNAL_SERVER_ERROR```."""
        the_owner = str(uuid.uuid4()).replace("-", "")

        def authenticate_patch(ignore_this_async_hmac_auth, callback):
            self.assertIsNotNone(callback)
            callback(True, owner=the_owner)

        name_of_method_to_patch = (
            "yar.auth_server.hmac."
            "async_hmac_auth.AsyncHMACAuth.authenticate"
        )
        with mock.patch(name_of_method_to_patch, authenticate_patch):
            def forward_patch(ignore_async_app_server_forwarder, callback):
                self.assertIsNotNone(callback)
                callback(False)

            name_of_method_to_patch = (
                "yar.auth_server.async_app_server_forwarder."
                "AsyncAppServerForwarder.forward"
            )
            with mock.patch(name_of_method_to_patch, forward_patch):
                http_client = httplib2.Http()
                response, content = http_client.request(
                    "http://localhost:%d/whatever" % type(self).auth_server.port,
                    "GET",
                    headers={"Authorization": "MAC ..."})
                self.assertIsNotNone(response)
                self.assertEqual(response.status, httplib.INTERNAL_SERVER_ERROR)

    def _test_forward_all_good(self, the_method, the_response_body=None):
        """Verify that on successful authentication the request is forwarded
        to the app server and the app server's response is correctly returned
        to the caller."""
        the_owner = str(uuid.uuid4()).replace("-", "")
        the_status_code = httplib.OK
        the_headers = {
            "X-Dave": str(uuid.uuid4()).replace("-", ""),
            "X-Bob": str(uuid.uuid4()).replace("-", ""),
            "X-Ben": str(uuid.uuid4()).replace("-", ""),
        }

        def authenticate_patch(ignore_this_async_hmac_auth, callback):
            self.assertIsNotNone(callback)
            callback(is_auth_ok=True, owner=the_owner)

        name_of_method_to_patch = (
            "yar.auth_server.hmac.async_hmac_auth."
            "AsyncHMACAuth.authenticate"
        )
        with mock.patch(name_of_method_to_patch, authenticate_patch):
            def forward_patch(ignore_async_app_server_forwarder, callback):
                self.assertIsNotNone(callback)
                callback(
                    is_ok=True,
                    http_status_code=the_status_code,
                    headers=the_headers,
                    body=the_response_body)

            name_of_method_to_patch = (
                "yar.auth_server.async_app_server_forwarder."
                "AsyncAppServerForwarder.forward"
            )
            with mock.patch(name_of_method_to_patch, forward_patch):
                http_client = httplib2.Http()
                response, content = http_client.request(
                    "http://localhost:%d/whatever" % type(self).auth_server.port,
                    the_method,
                    headers={"Authorization": "MAC ..."})
                self.assertIsNotNone(response)
                self.assertEqual(response.status, the_status_code)

    def test_forward_all_good_get(self):
        self._test_forward_all_good("GET", str(uuid.uuid4()).replace("-", ""))

    def test_forward_all_good_post(self):
        self._test_forward_all_good("POST")

    def test_forward_all_good_put(self):
        self._test_forward_all_good("PUT")

    def test_forward_all_good_delete(self):
        self._test_forward_all_good("DELETE")
