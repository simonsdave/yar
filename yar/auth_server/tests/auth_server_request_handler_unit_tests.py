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
from yar.auth_server.auth_server_request_handler import auth_failure_detail_header_name
from yar.auth_server.auth_server_request_handler import debug_header_prefix


class AuthServerRequestHanlderTestCase(tornado.testing.AsyncHTTPTestCase):
    """Unit tests for ```auth_server_request_handler.RequestHandler```."""

    def get_app(self):
        handlers = [
            (
                auth_server_request_handler.url_spec,
                auth_server_request_handler.RequestHandler
            ),
        ]
        self.app = tornado.web.Application(handlers=handlers)
        return self.app

    def _get_auth_failure_detail(self, response):
        """Search thru ```response```'s headers and if the
        auth failure detail header is found return a tuple
        that's the auth failure detail header's name and value."""
        for key, value in response.headers.iteritems():
            if auth_failure_detail_header_name.lower() == key.lower():
                return (key, value)
        return (None, None)

    def assertAuthFailureDetail(self, response, auth_failure_detail):
        """Assert an authorization failure detail HTTP header appears
        in ```response``` with a value equal to ```auth_failure_detail```."""
        (key, value) = self._get_auth_failure_detail(response)
        self.assertIsNotNone(key)
        self.assertIsNotNone(value)
        self.assertEqual(int(value), auth_failure_detail)

    def assertNoAuthFailureDetail(self, response):
        """Assert *no* authorization failure detail HTTP header
        appears in ```response```."""
        (key, value) = self._get_auth_failure_detail(response)
        self.assertIsNone(key)
        self.assertIsNone(value)

    def _get_auth_failure_debug_details(self, response):
        """Search thru ```response```'s headers and extract all
        auth failure debug headers found return as a dict
        with header's name as dict's key and header's value as
        the corresponding value."""
        # :TODO: look at all the 'lower()' calls in the code below!
        # What is DAS doing wrong?
        rv = {}
        for key, value in response.headers.iteritems():
            if key.lower().startswith(debug_header_prefix.lower()):
                if auth_failure_detail_header_name.lower() != key.lower():
                    rv[key[len(debug_header_prefix):].lower()] = value 
        return rv

    def assertAuthFailureDebugDetails(self, response, auth_failure_debug_details):
        """Assert specific authorization failure debug HTTP headers
        appear in ```response```."""
        self.assertEqual(
            auth_failure_debug_details,
            self._get_auth_failure_debug_details(response))

    def assertNoAuthFailureDebugDetails(self, response):
        """Assert *no* authorization failure debug HTTP headers
        appear in ```response```."""
        auth_failure_debug_details = self._get_auth_failure_debug_details(response)
        self.assertTrue(0 == len(auth_failure_debug_details))

    def test_no_authorization_header(self):
        """This test confirms that authentication fails if no Authorization
        header is supplied in the auth server's."""

        # setting _include_auth_failure_debug_details to True forces
        # the auth server to include auth failure details in response
        auth_server_request_handler._include_auth_failure_debug_details = True

        response = self.fetch("/", method="GET", headers={})
        self.assertEqual(response.code, httplib.UNAUTHORIZED)
        self.assertAuthFailureDetail(
            response,
            auth_server_request_handler.AUTH_FAILURE_DETAIL_NO_AUTH_HEADER)

    def test_invalid_authorization_header(self):
        """This test confirms that authentication fails if an Authorization
        header is supplied but it contains an unrecognized authententication
        scheme."""

        # setting _include_auth_failure_debug_details to True forces
        # the auth server to include auth failure details in response
        auth_server_request_handler._include_auth_failure_debug_details = True

        response = self.fetch("/", method="GET", headers={"Authorization": "DAVE"})
        self.assertEqual(response.code, httplib.UNAUTHORIZED)
        self.assertAuthFailureDetail(
            response,
            auth_server_request_handler.AUTH_FAILURE_DETAIL_UNKNOWN_AUTHENTICATION_SCHEME)

    def test_auth_failure_detail_correctly_in_auth_server_response(self):
        """This test confirms that when an authenticator
        supplies authentication failure detail that the failure
        detail is in the auth server's HTTP response as an HTTP header
        if the appropriate configuration is enabled."""

        the_auth_failure_detail = auth_server_request_handler.AUTH_FAILURE_DETAIL_FOR_TESTING

        the_auth_failure_debug_details = {
            str(uuid.uuid4()).replace("-", ""): str(uuid.uuid4()).replace("-", ""),
            str(uuid.uuid4()).replace("-", ""): str(uuid.uuid4()).replace("-", ""),
            str(uuid.uuid4()).replace("-", ""): str(uuid.uuid4()).replace("-", ""),
        }

        def authenticate_patch(authenticator, callback):
            callback(
                is_auth_ok=False,
                auth_failure_detail=the_auth_failure_detail,
                auth_failure_debug_details=the_auth_failure_debug_details)

        name_of_method_to_patch = (
            "yar.auth_server.hmac."
            "async_hmac_auth.AsyncHMACAuth.authenticate"
        )
        with mock.patch(name_of_method_to_patch, authenticate_patch):
            # step #1 ...

            # setting _include_auth_failure_debug_details to True forces
            # the auth server to include auth failure details in response
            auth_server_request_handler._include_auth_failure_debug_details = True

            response = self.fetch("/", method="GET", headers={"Authorization": "MAC ..."})
            self.assertEqual(response.code, httplib.UNAUTHORIZED)
            self.assertAuthFailureDetail(response, the_auth_failure_detail)
            self.assertAuthFailureDebugDetails(response, the_auth_failure_debug_details)

            # step #2 ...

            # setting _include_auth_failure_debug_details to False forces
            # the auth server to *not* include auth failure details in response
            auth_server_request_handler._include_auth_failure_debug_details = False

            response = self.fetch("/", method="GET", headers={"Authorization": "MAC ..."})
            self.assertEqual(response.code, httplib.UNAUTHORIZED)
            self.assertNoAuthFailureDetail(response)
            self.assertNoAuthFailureDebugDetails(response)

    def test_forward_to_app_server_failed(self):
        """Verify that when async the foward to the app server fails,
        that the response is ```httplib.INTERNAL_SERVER_ERROR```."""
        the_owner = str(uuid.uuid4()).replace("-", "")

        def authenticate_patch(authenticator, callback):
            callback(is_auth_ok=True, owner=the_owner)

        name_of_method_to_patch = (
            "yar.auth_server.hmac."
            "async_hmac_auth.AsyncHMACAuth.authenticate"
        )
        with mock.patch(name_of_method_to_patch, authenticate_patch):

            def forward_patch(async_app_server_forwarder, callback):
                callback(is_ok=False)

            name_of_method_to_patch = (
                "yar.auth_server.async_app_server_forwarder."
                "AsyncAppServerForwarder.forward"
            )
            with mock.patch(name_of_method_to_patch, forward_patch):

                response = self.fetch(
                    "/",
                    method="GET",
                    headers={"Authorization": "MAC ..."})

                self.assertIsNotNone(response)
                self.assertEqual(response.code, httplib.INTERNAL_SERVER_ERROR)

    def _test_forward_all_good(self, the_method, the_request_body, the_response_body):
        """Happy path verification of forwarding request to app server
        after authentication is successful."""

        the_owner = str(uuid.uuid4()).replace("-", "")
        the_status_code = httplib.OK
        the_response_headers = {
            "X-Dave": str(uuid.uuid4()).replace("-", ""),
            "X-Bob": str(uuid.uuid4()).replace("-", ""),
            "X-Ben": str(uuid.uuid4()).replace("-", ""),
        }

        def authenticate_patch(ignore_this_async_hmac_auth, callback):
            self.assertIsNotNone(callback)
            callback(is_auth_ok=True, owner=the_owner)

        name_of_method_to_patch = (
            "yar.auth_server.hmac."
            "async_hmac_auth.AsyncHMACAuth.authenticate"
        )
        with mock.patch(name_of_method_to_patch, authenticate_patch):

            def forward_patch(async_app_server_forwarder, callback):
                callback(
                    is_ok=True,
                    http_status_code=the_status_code,
                    headers=the_response_headers,
                    body=the_response_body)

            name_of_method_to_patch = (
                "yar.auth_server.async_app_server_forwarder."
                "AsyncAppServerForwarder.forward"
            )
            with mock.patch(name_of_method_to_patch, forward_patch):

                response = self.fetch(
                    "/",
                    method=the_method,
                    body=the_request_body,
                    headers={"Authorization": "MAC ..."})

                self.assertIsNotNone(response)
                self.assertEqual(response.code, the_status_code)
                # :TODO: what about response body & response headers?

    def test_forward_all_good_get(self):
        self._test_forward_all_good(
            "GET",
            None,
            str(uuid.uuid4()).replace("-", ""))

    def test_forward_all_good_post(self):
        self._test_forward_all_good(
            "POST",
            "",
            None)

    def test_forward_all_good_put(self):
        self._test_forward_all_good(
            "PUT",
            "",
            None)

    def test_forward_all_good_delete(self):
        self._test_forward_all_good(
            "DELETE",
            None,
            None)

    # :TODO: need test to verify MAC Authorization header uses MAC Authenticator
    # :TODO: need test to verify BASIC Authorization header uses Basic Authenticator
