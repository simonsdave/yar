"""This module implements unit tests for the key server's
async_creds_retriever module."""

import httplib
import os
import sys
import uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mock

import mac
import yar_test_util

import async_creds_retriever
import ks_util

class TestCaseAsyncCredsRetriever(yar_test_util.TestCase):
    """A collection of unit tests for the key server's
    async_creds_retriever module."""

    _key_store = "dave:42"

    def _test_error_from_async_req_to_key_store(
        self,
        the_is_ok,
        the_code,
        the_body):

        self.the_mac_key_identifier = mac.MACKeyIdentifier.generate()

        def async_req_to_key_store_patch(
            acr,
            path,
            method,
            body,
            callback):

            self.assertIsNotNone(acr)

            self.assertIsNotNone(path)
            self.assertEqual(path, self.the_mac_key_identifier)

            self.assertIsNotNone(method)
            self.assertEqual(method, "GET")

            self.assertIsNone(body)

            self.assertIsNotNone(callback)
            callback(is_ok=the_is_ok, code=the_code, body=the_body)

        def on_async_create_done(creds, is_creds_collection):
            self.assertIsNone(creds)
            self.assertIsNone(is_creds_collection)

        name_of_method_to_patch = "ks_util.AsyncAction.async_req_to_key_store"
        with mock.patch(name_of_method_to_patch, async_req_to_key_store_patch):
            acr = async_creds_retriever.AsyncCredsRetriever(type(self)._key_store)
            acr.fetch(
                callback=on_async_create_done,
                mac_key_identifier=self.the_mac_key_identifier)

    def test_is_ok_error_from_async_req_to_key_store(self):
        self._test_error_from_async_req_to_key_store(
            the_is_ok=False,
            the_code=httplib.OK,
            the_body={})

    def test_http_status_code_error_from_async_req_to_key_store(self):
        self._test_error_from_async_req_to_key_store(
            the_is_ok=True,
            the_code=httplib.INTERNAL_SERVER_ERROR,
            the_body={})

    def test_body_error_from_async_req_to_key_store(self):
        self._test_error_from_async_req_to_key_store(
            the_is_ok=True,
            the_code=httplib.OK,
            the_body=None)

    def _test_ok_on_mac_key_identifier_request_to_key_store(
        self,
        the_is_filter_out_deleted,
        the_is_filter_out_non_model_properties):

        the_body = {
            "_id": "9010212ebe184b13aecbd5ca5d72ae64",
            "_rev": "1-c81488ccbec47b14cec7010e18459a16",
            "is_deleted": True,
            "mac_algorithm": mac.MAC.algorithm,
            "mac_key": mac.MACKey.generate(),
            "mac_key_identifier": mac.MACKeyIdentifier.generate(),
            "owner": "dave@example.com",
            "type": "cred_v1.0",
        }

        def async_req_to_key_store_patch(
            acr,
            path,
            method,
            body,
            callback):

            self.assertIsNotNone(acr)

            self.assertIsNotNone(path)
            self.assertEqual(path, the_body["mac_key_identifier"])

            self.assertIsNotNone(method)
            self.assertEqual(method, "GET")

            self.assertIsNone(body)

            self.assertIsNotNone(callback)
            callback(is_ok=True, code=httplib.OK, body=the_body)

        def on_async_create_done(creds, is_creds_collection):
            if the_is_filter_out_deleted:
                self.assertIsNone(creds)
            else:
                self.assertIsNotNone(creds)
                if the_is_filter_out_non_model_properties:
                    self.assertEqual(
                        creds,
                        ks_util.filter_out_non_model_creds_properties(the_body))
                else:
                    self.assertEqual(creds, the_body)

            self.assertIsNotNone(is_creds_collection)
            self.assertFalse(is_creds_collection)

        name_of_method_to_patch = "ks_util.AsyncAction.async_req_to_key_store"
        with mock.patch(name_of_method_to_patch, async_req_to_key_store_patch):
            acr = async_creds_retriever.AsyncCredsRetriever(type(self)._key_store)
            acr.fetch(
                callback=on_async_create_done,
                mac_key_identifier=the_body["mac_key_identifier"],
                owner=None,
                is_filter_out_deleted=the_is_filter_out_deleted,
                is_filter_out_non_model_properties=the_is_filter_out_non_model_properties)

    def test_ok_on_mac_key_identifier_request_to_key_store_no_filtering(self):
        self._test_ok_on_mac_key_identifier_request_to_key_store(
            the_is_filter_out_deleted=False,
            the_is_filter_out_non_model_properties=False)

    def test_ok_on_mac_key_identifier_request_to_key_store_filter_non_model(self):
        self._test_ok_on_mac_key_identifier_request_to_key_store(
            the_is_filter_out_deleted=False,
            the_is_filter_out_non_model_properties=True)

    def test_ok_on_mac_key_identifier_request_to_key_store_filter_deleted(self):
        self._test_ok_on_mac_key_identifier_request_to_key_store(
            the_is_filter_out_deleted=True,
            the_is_filter_out_non_model_properties=False)
