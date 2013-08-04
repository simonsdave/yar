"""This module implements the unit tests for the auth server's
async_hmac_auth module."""

import httplib
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mock
import tornado.httputil

import mac
import yar_test_util

import async_hmac_auth

class TestAsyncHMACAuth(yar_test_util.TestCase):

    _maxage = 30

    @classmethod
    def setUpClass(cls):
        async_hmac_auth.maxage = cls._maxage

    @classmethod
    def tearDownClass(cls):
        pass

    def test_no_authorization_header(self):
        """When a request contains no Authorization HTTP header, confirm that
        ```async_hmac_auth.AsyncHMACAuth``` tags this as an authorization
        failure with ```async_hmac_auth.AUTH_FAILURE_DETAIL_NO_AUTH_HEADER```
        detailed error code."""

        def on_auth_done(is_auth_ok, auth_failure_detail):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(
                auth_failure_detail,
                async_hmac_auth.AUTH_FAILURE_DETAIL_NO_AUTH_HEADER)

        request = mock.Mock()
        request.headers = tornado.httputil.HTTPHeaders()

        aha = async_hmac_auth.AsyncHMACAuth(
            request=request,
            generate_debug_headers=False)
        aha.validate(on_auth_done)

    def test_invalid_authorization_header(self):
        """When a request contains an invalid Authorization HTTP header,
        confirm that ```async_hmac_auth.AsyncHMACAuth``` tags this as an
        authorization failure with
        ```async_hmac_auth.AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER```
        detailed error code."""

        def on_auth_done(is_auth_ok, auth_failure_detail):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(
                auth_failure_detail,
                async_hmac_auth.AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER)

        request = mock.Mock()
        request.headers = tornado.httputil.HTTPHeaders({
            "Authorization": "DAVE WAS HERE",
        })

        aha = async_hmac_auth.AsyncHMACAuth(
            request=request,
            generate_debug_headers=False)
        aha.validate(on_auth_done)

    def _test_timestamp(self, ts_adjustment, expected_auth_failure_detail):
        """When a request contains Authorization HTTP header with a
        timestamp that's old or in the fture,
        confirm that ```async_hmac_auth.AsyncHMACAuth``` tags this as an
        authorization failure with ```expected_auth_failutre_detail```
        detailed error code."""

        def on_auth_done(is_auth_ok, auth_failure_detail):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(auth_failure_detail, expected_auth_failure_detail)

        auth_header_value = mac.AuthHeaderValue(
            mac_key_identifier=mac.MACKeyIdentifier.generate(),
            ts=mac.Timestamp(int(mac.Timestamp.generate()) + ts_adjustment),
            nonce=mac.Nonce.generate(),
            ext=mac.Ext.generate(content_type=None, body=None),
            mac=mac.MAC("0123456789"))

        request = mock.Mock()
        request.headers = tornado.httputil.HTTPHeaders({
            "Authorization": str(auth_header_value),
        })

        aha = async_hmac_auth.AsyncHMACAuth(
            request=request,
            generate_debug_headers=False)
        aha.validate(on_auth_done)

    def test_timestamp_in_future(self):
        """When a request contains Authorization HTTP header with a
        timestamp that's in the future,
        confirm that ```async_hmac_auth.AsyncHMACAuth``` tags this as an
        authorization failure with
        ```async_hmac_auth.AUTH_FAILURE_DETAIL_TS_IN_FUTURE```
        detailed error code."""
        self._test_timestamp(
            1000,
            async_hmac_auth.AUTH_FAILURE_DETAIL_TS_IN_FUTURE)

    def test_timestamp_in_past(self):
        """When a request contains Authorization HTTP header with a
        timestamp that's in the past,
        confirm that ```async_hmac_auth.AsyncHMACAuth``` tags this as an
        authorization failure with
        ```async_hmac_auth.AUTH_FAILURE_DETAIL_TS_OLD```
        detailed error code."""
        self._test_timestamp(
            -1000,
            async_hmac_auth.AUTH_FAILURE_DETAIL_TS_OLD)

    def test_nonce_reused(self):
        """When a request contains Authorization HTTP header with a
        nonce that's been seen before,
        confirm that ```async_hmac_auth.AsyncHMACAuth``` tags this as an
        authorization failure with
        ```async_hmac_auth.AUTH_FAILURE_DETAIL_NONCE_REUSED```
        detailed error code."""

        def on_auth_done(is_auth_ok, auth_failure_detail):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(
                auth_failure_detail,
                async_hmac_auth.AUTH_FAILURE_DETAIL_NONCE_REUSED)

        def async_nonce_checker_fetch_patch(
            ignore_async_nonce_checker,
            callback,
            mac_key_identifier,
            nonce):
            callback(False)

        name_of_method_to_patch = "async_nonce_checker.AsyncNonceChecker.fetch"
        with mock.patch(name_of_method_to_patch, async_nonce_checker_fetch_patch):
            auth_header_value = mac.AuthHeaderValue(
                mac_key_identifier=mac.MACKeyIdentifier.generate(),
                ts=mac.Timestamp.generate(),
                nonce=mac.Nonce.generate(),
                ext=mac.Ext.generate(content_type=None, body=None),
                mac=mac.MAC("0123456789"))

            request = mock.Mock()
            request.headers = tornado.httputil.HTTPHeaders({
                "Authorization": str(auth_header_value),
            })

            aha = async_hmac_auth.AsyncHMACAuth(
                request=request,
                generate_debug_headers=False)
            aha.validate(on_auth_done)

    def test_creds_not_found(self):
        """When a request contains Authorization HTTP header with a
        mac key identifier that the key server doesn't know about,
        confirm that ```async_hmac_auth.AsyncHMACAuth``` tags this as an
        authorization failure with
        ```async_hmac_auth.AUTH_FAILURE_DETAIL_CREDS_NOT_FOUND```
        detailed error code."""

        def on_auth_done(is_auth_ok, auth_failure_detail):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(
                auth_failure_detail,
                async_hmac_auth.AUTH_FAILURE_DETAIL_CREDS_NOT_FOUND)

        def async_nonce_checker_fetch_patch(
            ignore_async_nonce_checker,
            callback,
            mac_key_identifier,
            nonce):
            callback(True)

        name_of_method_to_patch = "async_nonce_checker.AsyncNonceChecker.fetch"
        with mock.patch(name_of_method_to_patch, async_nonce_checker_fetch_patch):

            def async_creds_retriever_fetch_patch(
                ignore_async_creds_retriever,
                callback,
                mac_key_identifier):
                callback(False, mac_key_identifier)

            name_of_method_to_patch = "async_creds_retriever.AsyncCredsRetriever.fetch"
            with mock.patch(name_of_method_to_patch, async_creds_retriever_fetch_patch):

                auth_header_value = mac.AuthHeaderValue(
                    mac_key_identifier=mac.MACKeyIdentifier.generate(),
                    ts=mac.Timestamp.generate(),
                    nonce=mac.Nonce.generate(),
                    ext=mac.Ext.generate(content_type=None, body=None),
                    mac=mac.MAC("0123456789"))

                request = mock.Mock()
                request.headers = tornado.httputil.HTTPHeaders({
                    "Authorization": str(auth_header_value),
                })

                aha = async_hmac_auth.AsyncHMACAuth(
                    request=request,
                    generate_debug_headers=False)
                aha.validate(on_auth_done)
