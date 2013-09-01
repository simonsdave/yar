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


    def _test_ok_on_owner_request_to_key_store(
        self,
        the_is_filter_out_deleted,
        the_is_filter_out_non_model_properties):

        the_owner = "dave@example.com"

        the_non_deleted_creds = [
            {
                "_id": "070a69935bd840e09029a74837dc4755", 
                "_rev": "1-f1a30395b5df30003421a8969b001be7", 
                "is_deleted": False, 
                "mac_algorithm": "hmac-sha-1", 
                "mac_key": "CHlFh7fIejF3NLmr73pCfqx3EL_xV2zDQgVcjRl45jM", 
                "mac_key_identifier": "070a69935bd840e09029a74837dc4755", 
                "owner": the_owner,
                "type": "cred_v1.0"
            }, 
            {
                "_id": "9c8411a78405460e825b5f4318ef9a57", 
                "_rev": "1-ee4cfcd905e7d98ee7d0ed30463a7a99", 
                "is_deleted": False, 
                "mac_algorithm": "hmac-sha-1", 
                "mac_key": "pyHpZ6auevEEHTkZDhfVf-uKHV_YPEH2lctZXL5j4QQ", 
                "mac_key_identifier": "9c8411a78405460e825b5f4318ef9a57", 
                "owner": the_owner,
                "type": "cred_v1.0"
            }, 
        ]

        the_deleted_creds = [
            {
                "_id": "e49df12a968f4340a6e5f06c43e868bb", 
                "_rev": "1-8cfdd40a34ecaf4944e790e6beb028c5", 
                "is_deleted": True, 
                "mac_algorithm": "hmac-sha-1", 
                "mac_key": "8m_yH35Q9iMEZx_OV5M136eJ4SJsTw0JO-Y6BS3scJY", 
                "mac_key_identifier": "e49df12a968f4340a6e5f06c43e868bb", 
                "owner": the_owner,
                "type": "cred_v1.0"
            },
        ]

        the_creds = the_non_deleted_creds + the_deleted_creds

        def _to_couchdb_fmt(creds):
            _id = creds["_id"]
            rv = {"id": _id, "key": _id, "value": creds}
            return rv

        the_body = {
            "offset": 0, 
            "rows": [_to_couchdb_fmt(x) for x in the_creds],
            "total_rows": len(the_creds)
        }

        def async_req_to_key_store_patch(
            acr,
            path,
            method,
            body,
            callback):

            self.assertIsNotNone(acr)

            expected_path_fmt = (
                '_design/creds/_view/by_owner?'
                'startkey="%s"'
                '&'
                'endkey="%s"'
            )
            expected_path = expected_path_fmt % (the_owner, the_owner)
            self.assertIsNotNone(path)
            self.assertEqual(path, expected_path)

            self.assertIsNotNone(method)
            self.assertEqual(method, "GET")

            self.assertIsNone(body)

            self.assertIsNotNone(callback)
            callback(is_ok=True, code=httplib.OK, body=the_body)

        def on_async_create_done(creds, is_creds_collection):
            self.assertIsNotNone(is_creds_collection)
            self.assertTrue(is_creds_collection)

            self.assertIsNotNone(creds)
            if the_is_filter_out_deleted:
                self.assertEqual(creds, the_non_deleted_creds)
            else:
                if the_is_filter_out_non_model_properties:
                    the_creds_filtered = [
                        ks_util.filter_out_non_model_creds_properties(x) for x in the_creds
                    ]
                    self.assertEqual(creds, the_creds_filtered)
                else:
                    self.assertEqual(creds, the_creds)

        name_of_method_to_patch = "ks_util.AsyncAction.async_req_to_key_store"
        with mock.patch(name_of_method_to_patch, async_req_to_key_store_patch):
            acr = async_creds_retriever.AsyncCredsRetriever(type(self)._key_store)
            acr.fetch(
                callback=on_async_create_done,
                mac_key_identifier=None,
                owner=the_owner,
                is_filter_out_deleted=the_is_filter_out_deleted,
                is_filter_out_non_model_properties=the_is_filter_out_non_model_properties)

    def test_ok_on_owner_request_to_key_store_no_filtering(self):
        self._test_ok_on_owner_request_to_key_store(
            the_is_filter_out_deleted=False,
            the_is_filter_out_non_model_properties=False)

    def test_ok_on_owner_request_to_key_store_filter_non_model(self):
        self._test_ok_on_owner_request_to_key_store(
            the_is_filter_out_deleted=False,
            the_is_filter_out_non_model_properties=True)

    def test_ok_on_owner_request_to_key_store_filter_deleted(self):
        self._test_ok_on_owner_request_to_key_store(
            the_is_filter_out_deleted=True,
            the_is_filter_out_non_model_properties=False)

    def test_ok_on_retrieve_all_request_to_key_store(self):
        """_test_ok_on_owner_request_to_key_store tests the bulk
        of this functionality - all the test is really here to do
        is confirm that the correct request is issued to the
        key server."""

        the_body = {
            "offset": 0, 
            "rows": [
                {
                    "id": "070a69935bd840e09029a74837dc4755", 
                    "key": "070a69935bd840e09029a74837dc4755", 
                    "value": {
                        "_id": "070a69935bd840e09029a74837dc4755", 
                        "_rev": "1-f1a30395b5df30003421a8969b001be7", 
                        "is_deleted": False, 
                        "mac_algorithm": "hmac-sha-1", 
                        "mac_key": "CHlFh7fIejF3NLmr73pCfqx3EL_xV2zDQgVcjRl45jM", 
                        "mac_key_identifier": "070a69935bd840e09029a74837dc4755", 
                        "owner": "dave@gmail.com", 
                        "type": "cred_v1.0"
                    }
                }, 
                {
                    "id": "9c8411a78405460e825b5f4318ef9a57", 
                    "key": "9c8411a78405460e825b5f4318ef9a57", 
                    "value": {
                        "_id": "9c8411a78405460e825b5f4318ef9a57", 
                        "_rev": "1-ee4cfcd905e7d98ee7d0ed30463a7a99", 
                        "is_deleted": False, 
                        "mac_algorithm": "hmac-sha-1", 
                        "mac_key": "pyHpZ6auevEEHTkZDhfVf-uKHV_YPEH2lctZXL5j4QQ", 
                        "mac_key_identifier": "9c8411a78405460e825b5f4318ef9a57", 
                        "owner": "dave@gmail.com", 
                        "type": "cred_v1.0"
                    }
                }, 
                {
                    "id": "e49df12a968f4340a6e5f06c43e868bb", 
                    "key": "e49df12a968f4340a6e5f06c43e868bb", 
                    "value": {
                        "_id": "e49df12a968f4340a6e5f06c43e868bb", 
                        "_rev": "1-8cfdd40a34ecaf4944e790e6beb028c5", 
                        "is_deleted": False, 
                        "mac_algorithm": "hmac-sha-1", 
                        "mac_key": "8m_yH35Q9iMEZx_OV5M136eJ4SJsTw0JO-Y6BS3scJY", 
                        "mac_key_identifier": "e49df12a968f4340a6e5f06c43e868bb", 
                        "owner": "dave@gmail.com", 
                        "type": "cred_v1.0"
                    }
                }
            ], 
            "total_rows": 3
        }

        def async_req_to_key_store_patch(
            acr,
            path,
            method,
            body,
            callback):

            self.assertIsNotNone(acr)

            self.assertIsNotNone(path)
            self.assertEqual(path, "_design/creds/_view/all")

            self.assertIsNotNone(method)
            self.assertEqual(method, "GET")

            self.assertIsNone(body)

            self.assertIsNotNone(callback)
            callback(is_ok=True, code=httplib.OK, body=the_body)

        def on_async_create_done(creds, is_creds_collection):
            pass

        name_of_method_to_patch = "ks_util.AsyncAction.async_req_to_key_store"
        with mock.patch(name_of_method_to_patch, async_req_to_key_store_patch):
            acr = async_creds_retriever.AsyncCredsRetriever(type(self)._key_store)
            acr.fetch(
                callback=on_async_create_done,
                mac_key_identifier=None,
                owner=None,
                is_filter_out_deleted=False,
                is_filter_out_non_model_properties=False)
