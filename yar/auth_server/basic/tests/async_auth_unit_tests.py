"""This module implements the unit tests for the auth server's
basic.async_auth module."""

import base64
import sys
import uuid

import mock
import tornado.httputil

from yar import basic
from yar.auth_server.basic import async_auth
from yar.tests import yar_test_util


class TestAsyncAuth(yar_test_util.TestCase):

    def test_no_authorization_header(self):
        """When a request contains no Authorization HTTP header, confirm that
        ```async_auth.AsyncAuth``` tags this as an authorization
        failure with ```async_auth.AUTH_FAILURE_DETAIL_NO_AUTH_HEADER```
        detailed error code."""

        def on_auth_done(
            is_auth_ok,
            auth_failure_detail=None,
            auth_failure_debug_details=None,
            owner=None):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(
                auth_failure_detail,
                async_auth.AUTH_FAILURE_DETAIL_NO_AUTH_HEADER)

        request = mock.Mock()
        request.headers = tornado.httputil.HTTPHeaders()

        aha = async_auth.Authenticator(request)
        aha.authenticate(on_auth_done)

    def test_invalid_authorization_header_001(self):
        """When a request contains an invalid Authorization HTTP header,
        confirm that ```async_auth.AsyncAuth``` tags this as an authorization
        failure with ```async_auth.AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER```
        detailed error code.

        With this test the authorization header's value is blank."""

        def on_auth_done(
            is_auth_ok,
            auth_failure_detail=None,
            auth_failure_debug_details=None,
            owner=None):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(
                auth_failure_detail,
                async_auth.AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER_FORMAT_PRE_DECODING)

        request = mock.Mock()
        request.headers = tornado.httputil.HTTPHeaders({
            "Authorization": "",
        })

        aha = async_auth.Authenticator(request)
        aha.authenticate(on_auth_done)

    def test_invalid_authorization_header_002(self):
        """When a request contains an invalid Authorization HTTP header,
        confirm that ```async_auth.AsyncAuth``` tags this as an authorization
        failure with ```async_auth.AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER```
        detailed error code.

        With this test the authorization header's value only has the correct
        authorization scheme."""

        def on_auth_done(
            is_auth_ok,
            auth_failure_detail=None,
            auth_failure_debug_details=None,
            owner=None):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(
                auth_failure_detail,
                async_auth.AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER_FORMAT_PRE_DECODING)

        request = mock.Mock()
        request.headers = tornado.httputil.HTTPHeaders({
            "Authorization": "BASIC",
        })

        aha = async_auth.Authenticator(request)
        aha.authenticate(on_auth_done)

    def test_invalid_authorization_header_003(self):
        """When a request contains an invalid Authorization HTTP header,
        confirm that ```async_auth.AsyncAuth``` tags this as an authorization
        failure with ```async_auth.AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER```
        detailed error code.

        With this test the base64 encoded authorization header's value
        has both an api and password but there should not be a password."""

        the_api_key = basic.APIKey.generate()
        the_password = str(uuid.uuid4()).replace("-", "")

        def on_auth_done(
            is_auth_ok,
            auth_failure_detail=None,
            auth_failure_debug_details=None,
            owner=None):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(
                auth_failure_detail,
                async_auth.AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER_FORMAT_POST_DECODING)

        api_key_colon_password = "%s:%s" % (the_api_key, the_password)
        auth_hdr_value = "BASIC %s" % base64.b64encode(api_key_colon_password)
        request = mock.Mock()
        request.headers = tornado.httputil.HTTPHeaders({
            "Authorization": auth_hdr_value,
        })

        aha = async_auth.Authenticator(request)
        aha.authenticate(on_auth_done)

    def test_invalid_authorization_header_004(self):
        """When a request contains an invalid Authorization HTTP header,
        confirm that ```async_auth.AsyncAuth``` tags this as an authorization
        failure with ```async_auth.AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER```
        detailed error code.

        With this test the authorization header's value is not correctly
        base64 encoded."""

        def on_auth_done(
            is_auth_ok,
            auth_failure_detail=None,
            auth_failure_debug_details=None,
            owner=None):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(
                auth_failure_detail,
                async_auth.AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER_BAD_ENCODING)

        request = mock.Mock()
        request.headers = tornado.httputil.HTTPHeaders({
            "Authorization": "BASIC u:p",
        })

        aha = async_auth.Authenticator(request)
        aha.authenticate(on_auth_done)

    def test_error_getting_creds(self):
        the_api_key = basic.APIKey.generate()
        the_owner = str(uuid.uuid4()).replace("-", "")

        def on_auth_done(
            is_auth_ok,
            auth_failure_detail=None,
            auth_failure_debug_details=None,
            owner=None):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(
                auth_failure_detail,
                async_auth.AUTH_FAILURE_DETAIL_ERROR_GETTING_CREDS)

        def fetch_patch(acr, callback):
            callback(False)

        name_of_method_to_patch = (
            "yar.auth_server.basic.async_creds_retriever."
            "AsyncCredsRetriever.fetch"
        )
        with mock.patch(name_of_method_to_patch, fetch_patch):
            api_key_colon = "%s:" % the_api_key
            auth_hdr_value = "BASIC %s" % base64.b64encode(api_key_colon)
            request = mock.Mock()
            request.headers = tornado.httputil.HTTPHeaders({
                "Authorization": auth_hdr_value,
            })

            aha = async_auth.Authenticator(request)
            aha.authenticate(on_auth_done)

    def test_creds_not_found(self):
        the_api_key = basic.APIKey.generate()
        the_owner = str(uuid.uuid4()).replace("-", "")

        def on_auth_done(
            is_auth_ok,
            auth_failure_detail=None,
            auth_failure_debug_details=None,
            owner=None):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(
                auth_failure_detail,
                async_auth.AUTH_FAILURE_DETAIL_CREDS_NOT_FOUND)

        def fetch_patch(acr, callback):
            owner = None
            callback(True, owner)

        name_of_method_to_patch = (
            "yar.auth_server.basic.async_creds_retriever."
            "AsyncCredsRetriever.fetch"
        )
        with mock.patch(name_of_method_to_patch, fetch_patch):
            api_key_colon = "%s:" % the_api_key
            auth_hdr_value = "BASIC %s" % base64.b64encode(api_key_colon)
            request = mock.Mock()
            request.headers = tornado.httputil.HTTPHeaders({
                "Authorization": auth_hdr_value,
            })

            aha = async_auth.Authenticator(request)
            aha.authenticate(on_auth_done)

    def test_all_good(self):
        the_api_key = basic.APIKey.generate()
        the_owner = str(uuid.uuid4()).replace("-", "")

        def on_auth_done(
            is_auth_ok,
            auth_failure_detail=None,
            auth_failure_debug_details=None,
            owner=None):

            self.assertIsNotNone(is_auth_ok)
            self.assertTrue(is_auth_ok)

            self.assertIsNotNone(owner)
            self.assertEqual(owner, the_owner)

        def fetch_patch(acr, callback):
            callback(True, the_owner)

        name_of_method_to_patch = (
            "yar.auth_server.basic.async_creds_retriever."
            "AsyncCredsRetriever.fetch"
        )
        with mock.patch(name_of_method_to_patch, fetch_patch):
            api_key_colon = "%s:" % the_api_key
            auth_hdr_value = "BASIC %s" % base64.b64encode(api_key_colon)
            request = mock.Mock()
            request.headers = tornado.httputil.HTTPHeaders({
                "Authorization": auth_hdr_value,
            })

            aha = async_auth.Authenticator(request)
            aha.authenticate(on_auth_done)
