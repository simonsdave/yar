"""This module implements the unit tests for the auth server's
async_hmac_auth module."""

import httplib
import os
import sys

import mock
import tornado.httputil

from yar.auth_server import async_hmac_auth
from yar import mac
from yar.tests import yar_test_util


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
            generate_auth_failure_debug_details=False)
        aha.authenticate(on_auth_done)

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
            generate_auth_failure_debug_details=False)
        aha.authenticate(on_auth_done)

    def _test_timestamp(self, ts_adjustment, expected_auth_failure_detail):
        """When a request contains Authorization HTTP header with a
        timestamp that's old or in the fture,
        confirm that ```async_hmac_auth.AsyncHMACAuth``` tags this as an
        authentication failure with ```expected_auth_failure_detail```
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
            generate_auth_failure_debug_details=False)
        aha.authenticate(on_auth_done)

    def test_timestamp_in_future(self):
        """When a request contains Authorization HTTP header with a
        timestamp that's in the future,
        confirm that ```async_hmac_auth.AsyncHMACAuth``` tags this as an
        authentication failure with
        ```async_hmac_auth.AUTH_FAILURE_DETAIL_TS_IN_FUTURE```
        detailed error code."""
        self._test_timestamp(
            1000,
            async_hmac_auth.AUTH_FAILURE_DETAIL_TS_IN_FUTURE)

    def test_timestamp_in_past(self):
        """When a request contains Authorization HTTP header with a
        timestamp that's in the past,
        confirm that ```async_hmac_auth.AsyncHMACAuth``` tags this as an
        authentication failure with
        ```async_hmac_auth.AUTH_FAILURE_DETAIL_TS_OLD```
        detailed error code."""
        self._test_timestamp(
            -1000,
            async_hmac_auth.AUTH_FAILURE_DETAIL_TS_OLD)

    def test_nonce_reused(self):
        """When a request contains Authorization HTTP header with a
        nonce that's been seen before,
        confirm that ```async_hmac_auth.AsyncHMACAuth``` tags this as an
        authentication failure with
        ```async_hmac_auth.AUTH_FAILURE_DETAIL_NONCE_REUSED```
        detailed error code."""

        def on_auth_done(is_auth_ok, auth_failure_detail):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(
                auth_failure_detail,
                async_hmac_auth.AUTH_FAILURE_DETAIL_NONCE_REUSED)

        def async_nonce_checker_fetch_patch(anc, callback):
            callback(False)

        name_of_method_to_patch = "yar.auth_server.async_nonce_checker.AsyncNonceChecker.fetch"
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
                generate_auth_failure_debug_details=False)
            aha.authenticate(on_auth_done)

    def test_creds_not_found(self):
        """When a request contains Authorization HTTP header with a
        mac key identifier that the key server doesn't know about,
        confirm that ```async_hmac_auth.AsyncHMACAuth``` tags this as an
        authentication failure with
        ```async_hmac_auth.AUTH_FAILURE_DETAIL_CREDS_NOT_FOUND```
        detailed error code."""

        the_mac_key_identifier = mac.MACKeyIdentifier.generate()

        def on_auth_done(is_auth_ok, auth_failure_detail):

            self.assertIsNotNone(is_auth_ok)
            self.assertFalse(is_auth_ok)

            self.assertIsNotNone(auth_failure_detail)
            self.assertEqual(
                auth_failure_detail,
                async_hmac_auth.AUTH_FAILURE_DETAIL_CREDS_NOT_FOUND)

        def async_nonce_checker_fetch_patch(anc, callback):
            callback(True)

        name_of_method_to_patch = "yar.auth_server.async_nonce_checker.AsyncNonceChecker.fetch"
        with mock.patch(name_of_method_to_patch, async_nonce_checker_fetch_patch):

            def async_creds_retriever_fetch_patch(acr, callback):
                callback(False, the_mac_key_identifier)

            name_of_method_to_patch = "yar.auth_server.async_hmac_creds_retriever.AsyncHMACCredsRetriever.fetch"
            with mock.patch(name_of_method_to_patch, async_creds_retriever_fetch_patch):

                auth_header_value = mac.AuthHeaderValue(
                    mac_key_identifier=the_mac_key_identifier,
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
                    generate_auth_failure_debug_details=False)
                aha.authenticate(on_auth_done)

    def _test_mac_good_or_bad(
        self,
        the_method,
        the_bad_mac,
        generate_auth_failure_debug_details):
        """When a request contains an Authorization HTTP header that
        correctly authenticates a caller."""

        the_owner = "das@example.com"
        the_mac_key_identifier = mac.MACKeyIdentifier.generate()
        the_mac_key = mac.MACKey.generate()
        the_mac_algorithm = mac.MAC.algorithm
        the_ts = mac.Timestamp.generate()
        the_nonce = mac.Nonce.generate()
        if "GET" == the_method:
            the_body = None
            the_content_type = None
        else:
            the_body = "bindle berry"
            the_content_type = "application/json; charset=utf8"
        the_ext = mac.Ext.generate(the_content_type, the_body)
        the_host="localhost"
        the_port=8080
        the_uri="/whatever.html"
        the_normalized_request_string = mac.NormalizedRequestString.generate(
            the_ts,
            the_nonce,
            the_method,
            the_uri,
            the_host,
            the_port,
            the_ext)
        if the_bad_mac is None:
            the_mac = mac.MAC.generate(
                the_mac_key,
                the_mac_algorithm,
                the_normalized_request_string)
        else:
            the_mac = the_bad_mac

        def async_nonce_checker_fetch_patch(anc, callback):
            callback(True)

        name_of_method_to_patch = "yar.auth_server.async_nonce_checker.AsyncNonceChecker.fetch"
        with mock.patch(name_of_method_to_patch, async_nonce_checker_fetch_patch):

            def async_creds_retriever_fetch_patch(acr, callback):
                self.assertIsNotNone(acr)
                is_ok = True
                is_deleted = False
                callback(
                    is_ok,
                    the_mac_key_identifier,
                    is_deleted,
                    the_mac_algorithm,
                    the_mac_key,
                    the_owner)

            name_of_method_to_patch = "yar.auth_server.async_hmac_creds_retriever.AsyncHMACCredsRetriever.fetch"
            with mock.patch(name_of_method_to_patch, async_creds_retriever_fetch_patch):

                auth_header_value = mac.AuthHeaderValue(
                    the_mac_key_identifier,
                    the_ts,
                    the_nonce,
                    the_ext,
                    the_mac)

                request = mock.Mock()
                request.method = the_method
                request.uri = the_uri
                request.headers = tornado.httputil.HTTPHeaders({
                    "Host": ("%s:%d" % (the_host, the_port)),
                    "Authorization": str(auth_header_value),
                })
                if the_content_type is not None:
                    request.headers["Content-type"] = the_content_type
                if the_body is not None:
                    request.body = the_body
                    request.headers["Content-Length"] = len(the_body)
                
                def on_auth_done(
                    is_auth_ok,
                    auth_failure_detail=None,
                    auth_failure_debug_details=None,
                    owner=None,
                    identifier=None):

                    self.assertIsNotNone(is_auth_ok)

                    if the_bad_mac is None:
                        self.assertTrue(is_auth_ok)

                        self.assertIsNone(auth_failure_detail)
                        self.assertIsNone(auth_failure_debug_details)

                        self.assertIsNotNone(owner)
                        self.assertEqual(owner, the_owner)

                        self.assertIsNotNone(identifier)
                        self.assertEqual(identifier, the_mac_key_identifier)
                    else:
                        self.assertFalse(is_auth_ok)

                        self.assertIsNotNone(auth_failure_detail)
                        self.assertEqual(
                            auth_failure_detail,
                            async_hmac_auth.AUTH_FAILURE_DETAIL_HMACS_DO_NOT_MATCH)

                        self.assertIsNotNone(auth_failure_debug_details)
                        if generate_auth_failure_debug_details:
                            self.assertTrue(0 < len(auth_failure_debug_details))
                        else:
                            self.assertTrue(0 == len(auth_failure_debug_details))

                        self.assertIsNone(owner)
                        self.assertIsNone(identifier)

                aha = async_hmac_auth.AsyncHMACAuth(
                    request=request,
                    generate_auth_failure_debug_details=generate_auth_failure_debug_details)
                aha.authenticate(on_auth_done)

    def test_mac_bad_and_do_not_generate_debug_details(self):
        self._test_mac_good_or_bad(
            the_method="GET",
            the_bad_mac="dave",
            generate_auth_failure_debug_details=False)

    def test_mac_bad_and_generate_debug_details(self):
        self._test_mac_good_or_bad(
            the_method="GET",
            the_bad_mac="dave",
            generate_auth_failure_debug_details=True)

    def test_mac_bad_on_post_and_generate_debug_details(self):
        self._test_mac_good_or_bad(
            the_method="POST",
            the_bad_mac="dave",
            generate_auth_failure_debug_details=True)

    def test_mac_good(self):
        self._test_mac_good_or_bad(
            the_method="GET",
            the_bad_mac=None,
            generate_auth_failure_debug_details=False)
