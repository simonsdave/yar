"""This module implements unit tests for the key server's ks_util module."""

import httplib
import json
import os
import sys
import uuid

import mock
import tornado.httputil

from yar.tests import yar_test_util
from yar.key_server import ks_util

class TestCaseFilterOutNonModelCredProperties(yar_test_util.TestCase):
    """A collection of unit tests for
    ks_util's filter_out_non_model_creds_properties()."""

    def test_creds_arg_is_none(self):
        creds = None
        self.assertIsNone(ks_util.filter_out_non_model_creds_properties(creds))

    def test_model_properties_are_not_filtered_out(self):
        creds = {
            "is_deleted": str(uuid.uuid4()).replace("-", ""),
            "mac_algorithm": str(uuid.uuid4()).replace("-", ""),
            "mac_key": str(uuid.uuid4()).replace("-", ""),
            "mac_key_identifier": str(uuid.uuid4()).replace("-", ""),
            "owner": str(uuid.uuid4()).replace("-", ""),
        }
        filtered_creds = ks_util.filter_out_non_model_creds_properties(creds)
        self.assertEqual(creds, filtered_creds)

    def test_non_model_properties_are_filtered_out(self):
        non_cred_properties = {
            "dave": str(uuid.uuid4()).replace("-", ""),
            "was": str(uuid.uuid4()).replace("-", ""),
            "here": str(uuid.uuid4()).replace("-", ""),
        }
        creds = {
            "is_deleted": str(uuid.uuid4()).replace("-", ""),
            "mac_algorithm": str(uuid.uuid4()).replace("-", ""),
            "mac_key": str(uuid.uuid4()).replace("-", ""),
            "mac_key_identifier": str(uuid.uuid4()).replace("-", ""),
            "owner": str(uuid.uuid4()).replace("-", ""),
        }
        combined_creds = z = dict(non_cred_properties.items() + creds.items())
        filtered_creds = ks_util.filter_out_non_model_creds_properties(combined_creds)
        self.assertEqual(creds, filtered_creds)

class TestCaseAsyncAction(yar_test_util.TestCase):
    """A collection of unit tests for ks_util's AsyncAction class."""

    _key_store = "dave:42"

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def _test_good(
        self,
        request_method,
        request_body_as_dict,
        response_body_as_dict):
        """This is a rather long but very useful utility method
        which enables complete testing of
        ```ks_util.AsyncAction.async_req_to_key_store```."""

        request_path = str(uuid.uuid4()).replace("-", "")
        response_body = json.dumps(response_body_as_dict) if response_body_as_dict else None

        def async_http_client_fetch_patch(http_client, request, callback):
            """This function is used to patch
            ```tornado.httpclient.AsyncHTTPClient.fetch``` so that when
            ```ks_util.AsyncAction.async_req_to_key_store``` calls
            ```tornado.httpclient.AsyncHTTPClient.fetch``` this test
            (or this function specifically) can get into the call stream."""

            self.assertIsNotNone(request)

            self.assertIsNotNone(request.url)
            expected_url = "http://%s/%s" % (type(self)._key_store, request_path)
            self.assertEqual(request.url, expected_url)

            self.assertIsNotNone(request.method)
            self.assertEqual(request.method, request_method)

            if request_body_as_dict:
                self.assertIsNotNone(request.body)
                self.assertEqual(
                    request_body_as_dict,
                    json.loads(request.body))
            else:
                self.assertIsNone(request.body)

            response = mock.Mock()
            response.error = None
            response.code = httplib.OK
            response.body = response_body
            response.headers = tornado.httputil.HTTPHeaders()
            if response.body:
                response.headers["Content-type"] = "application/json"
                response.headers["Content-length"] = str(len(response_body))

            self.assertIsNotNone(callback)
            callback(response)

        def on_async_req_to_key_store_done(is_ok, http_status_code=None, body=None):
            """Called when ```ks_util.AsyncAction.async_req_to_key_store```
            completes."""
            self.assertTrue(is_ok)

            self.assertIsNotNone(http_status_code)
            self.assertEqual(http_status_code, httplib.OK)

            if response_body_as_dict:
                self.assertIsNotNone(body)
                self.assertEqual(type(body), dict)
                self.assertEqual(body, response_body_as_dict)
            else:
                self.assertIsNone(body)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            aa = ks_util.AsyncAction(type(self)._key_store)
            aa.async_req_to_key_store(
                request_path,
                request_method,
                request_body_as_dict,
                on_async_req_to_key_store_done)

    def test_good_get(self):
        request_method = "GET"
        request_body_as_dict = None
        response_body_as_dict = {
            "_id": "a6dc9a78867d4dee95d58adefa87c1a1",
            "_rev": "1-89d4dd4616978a4a2af907228af0cb69",
            "is_deleted": False,
            "mac_algorithm": "hmac-sha-1",
            "mac_key": "XShLQP_vY8zZTlABKoFh9a7ALSdyEeP3WJaSUlCYVW4",
            "mac_key_identifier": "a6dc9a78867d4dee95d58adefa87c1a1",
            "owner": "bindleberry@example.com",
            "type": "creds_v1.0",
        }
        self._test_good(
            request_method,
            request_body_as_dict,
            response_body_as_dict)

    def test_good_put(self):
        request_method = "PUT"
        request_body_as_dict = {
            "_id": "a6dc9a78867d4dee95d58adefa87c1a1",
            "_rev": "1-89d4dd4616978a4a2af907228af0cb69",
            "is_deleted": False,
            "mac_algorithm": "hmac-sha-1",
            "mac_key": "XShLQP_vY8zZTlABKoFh9a7ALSdyEeP3WJaSUlCYVW4",
            "mac_key_identifier": "a6dc9a78867d4dee95d58adefa87c1a1",
            "owner": "bindleberry@example.com",
            "type": "creds_v1.0",
        }
        response_body_as_dict = None
        self._test_good(
            request_method,
            request_body_as_dict,
            response_body_as_dict)

    def test_error_in_response(self):
        """This test verifies the behavior of
        ```ks_util.AsyncAction.async_req_to_key_store```
        when an error is returned by the HTTP request
        to the key store."""

        def async_http_client_fetch_patch(http_client, request, callback):
            """This function is used to patch
            ```tornado.httpclient.AsyncHTTPClient.fetch``` so that when
            ```ks_util.AsyncAction.async_req_to_key_store``` calls
            ```tornado.httpclient.AsyncHTTPClient.fetch``` this test
            (or this function specifically) can get into the call stream."""

            response = mock.Mock()
            response.code = httplib.INTERNAL_SERVER_ERROR
            response.error = str(uuid.uuid4()).replace("-", "")
            response.body = None
            response.headers = tornado.httputil.HTTPHeaders()

            callback(response)

        def on_async_req_to_key_store_done(is_ok, http_status_code=None, body=None):
            """Called when ```ks_util.AsyncAction.async_req_to_key_store```
            completes."""
            self.assertFalse(is_ok)

            self.assertIsNone(http_status_code)
            self.assertIsNone(body)

        name_of_method_to_patch = "tornado.httpclient.AsyncHTTPClient.fetch"
        with mock.patch(name_of_method_to_patch, async_http_client_fetch_patch):
            aa = ks_util.AsyncAction(type(self)._key_store)
            aa.async_req_to_key_store(
                "dave",
                "GET",
                None,
                on_async_req_to_key_store_done)

