"""This module contains unit tests for the auth server's auth_server module."""

import httplib
import logging
import os
import sys
import unittest
import uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httplib2
import mock
import tornado.httpserver
import tornado.httputil
import tornado.web

import yar_test_util

import auth_server


_logger = logging.getLogger(__name__)


"""```_auth_method_name_to_patch``` and ```_forward_method_name_to_patch```
are the names of methods that need to be mocked so that auth_server's
functionality can be isolated for unit testing."""
_auth_method_name_to_patch = "async_hmac_auth.AsyncHMACAuth.authenticate"
_forward_method_name_to_patch = "async_app_server_forwarder.AsyncAppServerForwarder.forward"


class AuthServer(yar_test_util.Server):
    """Mock auth server."""

    def __init__(self, generate_debug_headers=False):
        """Creates an instance of the auth server and starts the
        server listenting on a random, available port."""
        yar_test_util.Server.__init__(self)

        auth_server.generate_debug_headers = generate_debug_headers

        http_server = tornado.httpserver.HTTPServer(auth_server._app)
        http_server.add_sockets([self.socket])

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
        auth_failure_detail_header_value = response.get(
            # :TODO: why do I have to do this lower()?
            auth_server.auth_failure_detail_header_name.lower(),
            None)
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
        and only these headers appear in ```response```."""
        self.assertIsNotNone(response)
        # :TODO: why do I have to do this lower()?
        debug_header_prefix_lower_case = auth_server.debug_header_prefix.lower()
        auth_failure_detail_header_name_lower_case = auth_server.auth_failure_detail_header_name.lower()
        def _is_debug_header_key(key):
            key_lower_case = key.lower()
            if not key_lower_case.startswith(debug_header_prefix_lower_case):
                return False
            if auth_failure_detail_header_name_lower_case == key_lower_case:
                return False
            return True

        debug_headers_in_response = {
            # :TODO: why do I have to do this lower()?
            k[len(debug_header_prefix_lower_case):]: v for k, v in response.iteritems() if _is_debug_header_key(k)
        }
        if debug_headers is None:
            print debug_headers_in_response
            self.assertTrue(0 == len(debug_headers_in_response))
        else:
            self.assertEqual(
                debug_headers,
                debug_headers_in_response)

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

        with mock.patch(_auth_method_name_to_patch, authenticate_patch):
            def forward_patch(ignore_async_app_server_forwarder, callback):
                """This should never be called when authentication fails."""
                self.assertTrue(False)

            with mock.patch(_forward_method_name_to_patch, forward_patch):
                http_client = httplib2.Http()
                response, content = http_client.request(
                    "http://localhost:%d/whatever" % self.__class__.auth_server.port,
                    "GET")
                self.assertIsNotNone(response)
                self.assertIsNotNone(response.status)
                self.assertEqual(response.status, httplib.UNAUTHORIZED)
                self.assertAuthorizationFailureDetail(response)
                self.assertAuthorizationDebugHeaders(response)

    def test_hmac_auth_failed_auth_failure_detail_in_auth_server_response(self):
        """This test confirms that when the authenication
        mechanism supplies authentication failure detail
        that the failure detail is in the auth server's HTTP
        response as an HTTP header."""

        the_auth_failure_detail = str(uuid.uuid4()).replace("-", "")

        def authenticate_patch(an_async_hmac_auth, callback):
            self.assertIsNotNone(an_async_hmac_auth)
            self.assertIsNotNone(callback)
            callback(
                is_auth_ok=False,
                auth_failure_detail=the_auth_failure_detail)

        with mock.patch(_auth_method_name_to_patch, authenticate_patch):
            def forward_patch(ignore_async_app_server_forwarder, callback):
                """This should never be called when authentication fails."""
                self.assertTrue(False)

            with mock.patch(_forward_method_name_to_patch, forward_patch):
                http_client = httplib2.Http()
                response, content = http_client.request(
                    "http://localhost:%d/whatever" % self.__class__.auth_server.port,
                    "GET")
                self.assertIsNotNone(response)
                self.assertIsNotNone(response.status)
                self.assertEqual(response.status, httplib.UNAUTHORIZED)
                self.assertAuthorizationFailureDetail(
                    response,
                    the_auth_failure_detail)
                self.assertAuthorizationDebugHeaders(response)

    def test_hmac_auth_failed_debug_headers_in_auth_server_response(self):
        """This test confirms that when the authenication
        mechanism supplies debug headers
        that the debug headers are the auth server's HTTP response."""

        prefix = auth_server.debug_header_prefix.lower()
        the_debug_headers = {
            str(uuid.uuid4()).replace("-", ""): str(uuid.uuid4()).replace("-", ""),
            str(uuid.uuid4()).replace("-", ""): str(uuid.uuid4()).replace("-", ""),
            str(uuid.uuid4()).replace("-", ""): str(uuid.uuid4()).replace("-", ""),
        }

        def authenticate_patch(an_async_hmac_auth, callback):
            self.assertIsNotNone(an_async_hmac_auth)
            self.assertIsNotNone(callback)
            callback(
                is_auth_ok=False,
                debug_headers=the_debug_headers)

        with mock.patch(_auth_method_name_to_patch, authenticate_patch):
            def forward_patch(ignore_async_app_server_forwarder, callback):
                """This should never be called when authentication fails."""
                self.assertTrue(False)

            with mock.patch(_forward_method_name_to_patch, forward_patch):
                http_client = httplib2.Http()
                response, content = http_client.request(
                    "http://localhost:%d/whatever" % self.__class__.auth_server.port,
                    "GET")
                self.assertIsNotNone(response)
                self.assertIsNotNone(response.status)
                self.assertEqual(response.status, httplib.UNAUTHORIZED)
                self.assertAuthorizationFailureDetail(response)
                self.assertAuthorizationDebugHeaders(
                    response,
                    the_debug_headers)

    def test_forward_to_app_server_failed(self):
        """Verify that when async the foward to the app server fails,
        that the response is ```httplib.INTERNAL_SERVER_ERROR```."""
        the_owner = str(uuid.uuid4()).replace("-", "")
        the_identifier = str(uuid.uuid4()).replace("-", "")

        def authenticate_patch(ignore_this_async_hmac_auth, callback):
            self.assertIsNotNone(callback)
            callback(True, owner=the_owner, identifier=the_identifier)

        with mock.patch(_auth_method_name_to_patch, authenticate_patch):
            def forward_patch(ignore_async_app_server_forwarder, callback):
                self.assertIsNotNone(callback)
                callback(False)

            with mock.patch(_forward_method_name_to_patch, forward_patch):
                http_client = httplib2.Http()
                response, content = http_client.request(
                    "http://localhost:%d/whatever" % self.__class__.auth_server.port,
                    "GET")
                self.assertIsNotNone(response)
                self.assertEqual(response.status, httplib.INTERNAL_SERVER_ERROR)

    def test_forward_all_good(self):
        """Verify that when async the foward to the app server fails,
        that the response is ```httplib.INTERNAL_SERVER_ERROR```."""
        the_owner = str(uuid.uuid4()).replace("-", "")
        the_identifier = str(uuid.uuid4()).replace("-", "")
        the_status_code = httplib.OK
        the_headers = {
            "X-Dave": str(uuid.uuid4()).replace("-", ""),
            "X-Bob": str(uuid.uuid4()).replace("-", ""),
            "X-Ben": str(uuid.uuid4()).replace("-", ""),
        }
        the_body = str(uuid.uuid4()).replace("-", "")

        def authenticate_patch(ignore_this_async_hmac_auth, callback):
            self.assertIsNotNone(callback)
            callback(
                is_auth_ok=True,
                owner=the_owner,
                identifier=the_identifier)

        with mock.patch(_auth_method_name_to_patch, authenticate_patch):
            def forward_patch(ignore_async_app_server_forwarder, callback):
                self.assertIsNotNone(callback)
                callback(
                    is_ok=True,
                    http_status_code=the_status_code,
                    headers=the_headers,
                    body=the_body)

            with mock.patch(_forward_method_name_to_patch, forward_patch):
                http_client = httplib2.Http()
                response, content = http_client.request(
                    "http://localhost:%d/whatever" % self.__class__.auth_server.port,
                    "GET")
                self.assertIsNotNone(response)
                self.assertEqual(response.status, the_status_code)
