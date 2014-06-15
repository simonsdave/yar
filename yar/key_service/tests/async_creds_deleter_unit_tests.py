"""This module implements unit tests for the key service's
async_creds_retriever module."""

import httplib
import os
import sys
import uuid

import mock

from yar.key_service import async_creds_deleter
from yar.util import mac
from yar.tests import yar_test_util


class TestCaseAsyncCredsDeleter(yar_test_util.TestCase):
    """A collection of whitebox unit tests for the key service's
    async_creds_deleter module."""

    _key_store = "dave:42"

    def test_creds_not_found(self):
        """Validates async_creds_deleter's behavior when
        AsyncCredsRetriever indicates the credentials being
        deleted don't exist in the key store."""

        the_key = uuid.uuid4().hex

        def async_creds_retriever_fetch_patch(
            acd,
            callback,
            key,
            is_filter_out_deleted):

            self.assertIsNotNone(acd)

            self.assertEqual(key, the_key)

            self.assertFalse(is_filter_out_deleted)

            self.assertIsNotNone(callback)
            callback(creds=None, is_creds_collection=None)

        def on_async_delete_done(is_ok):
            self.assertIsNotNone(is_ok)
            self.assertFalse(is_ok)

        name_of_method_to_patch = (
            "yar.key_service.async_creds_retriever."
            "AsyncCredsRetriever.fetch"
        )
        with mock.patch(name_of_method_to_patch, async_creds_retriever_fetch_patch):
            acd = async_creds_deleter.AsyncCredsDeleter(type(self)._key_store)
            acd.delete(key=the_key, callback=on_async_delete_done)

    def test_already_deleted_creds(self):
        """Validates async_creds_deleter's behavior when
        the credentials being deleted have already been
        deleted."""

        the_creds = {
            "_id": "9010212ebe184b13aecbd5ca5d72ae64",
            "_rev": "1-c81488ccbec47b14cec7010e18459a16",
            "is_deleted": True,
            "mac": {
                "mac_algorithm": mac.MAC.algorithm,
                "mac_key": mac.MACKey.generate(),
                "mac_key_identifier": mac.MACKeyIdentifier.generate(),
            },
            "principal": "dave@example.com",
            "type": "creds_v1.0",
        }

        def async_creds_retriever_fetch_patch(
            acd,
            callback,
            key,
            is_filter_out_deleted):

            self.assertIsNotNone(acd)

            self.assertEqual(key, the_creds["mac"]["mac_key_identifier"])

            self.assertFalse(is_filter_out_deleted)

            self.assertIsNotNone(callback)
            callback(creds=the_creds, is_creds_collection=False)

        def async_req_to_key_store_patch(
            acd,
            path,
            method,
            body,
            callback):
            """this patch is here to make sure we don't try to update
            creds that have already been deleted."""
            self.assertFalse(True)

        def on_async_delete_done(is_ok):
            self.assertIsNotNone(is_ok)
            self.assertTrue(is_ok)

        name_of_method_to_patch = "yar.key_service.async_creds_retriever.AsyncCredsRetriever.fetch"
        with mock.patch(name_of_method_to_patch, async_creds_retriever_fetch_patch):
            name_of_method_to_patch = "yar.key_service.ks_util.AsyncAction.async_req_to_key_store"
            with mock.patch(name_of_method_to_patch, async_req_to_key_store_patch):
                acd = async_creds_deleter.AsyncCredsDeleter(type(self)._key_store)
                acd.delete(
                    key=the_creds["mac"]["mac_key_identifier"],
                    callback=on_async_delete_done)

    def _test_creds_update_failure(self, the_is_ok, the_code):
        """Validates async_creds_deleter's behavior on
        failed update of credentials being deleted.

        This is a generic utility method called
        by actual unit test methods because there are
        a couple of different ways in which the update
        (ks_util.AsyncAction.async_req_to_key_store
        specifically) can return results that indicate
        failure."""

        the_creds = {
            "_id": "9010212ebe184b13aecbd5ca5d72ae64",
            "_rev": "1-c81488ccbec47b14cec7010e18459a16",
            "is_deleted": False,
            "mac": {
                "mac_algorithm": mac.MAC.algorithm,
                "mac_key": mac.MACKey.generate(),
                "mac_key_identifier": mac.MACKeyIdentifier.generate(),
            },
            "principal": "dave@example.com",
            "type": "creds_v1.0",
        }

        def async_creds_retriever_fetch_patch(
            acd,
            callback,
            key,
            is_filter_out_deleted):

            self.assertIsNotNone(acd)

            self.assertEqual(key, the_creds["mac"]["mac_key_identifier"])

            self.assertFalse(is_filter_out_deleted)

            self.assertIsNotNone(callback)
            callback(creds=the_creds, is_creds_collection=False)

        def async_req_to_key_store_patch(
            acd,
            path,
            method,
            body,
            callback):

            self.assertIsNotNone(acd)

            self.assertIsNotNone(path)
            self.assertEqual(the_creds["_id"], path)

            self.assertIsNotNone(method)
            self.assertEqual(method, "PUT")

            self.assertIsNotNone(callback)
            if the_is_ok:
                callback(is_ok=True, code=the_code, body=None)
            else:
                callback(is_ok=False)

        def on_async_delete_done(is_ok):
            self.assertIsNotNone(is_ok)
            self.assertFalse(is_ok)

        name_of_method_to_patch = (
            "yar.key_service.async_creds_retriever."
            "AsyncCredsRetriever.fetch"
        )
        with mock.patch(name_of_method_to_patch, async_creds_retriever_fetch_patch):
            name_of_method_to_patch = (
                "yar.key_service.ks_util."
                "AsyncAction.async_req_to_key_store"
            )
            with mock.patch(name_of_method_to_patch, async_req_to_key_store_patch):
                acd = async_creds_deleter.AsyncCredsDeleter(type(self)._key_store)
                acd.delete(
                    key=the_creds["mac"]["mac_key_identifier"],
                    callback=on_async_delete_done)

    def test_creds_update_failure_bad_is_ok(self):
        """Validates async_creds_deleter's behavior when
        the update of credentials being deleted fail."""
        self._test_creds_update_failure(
            the_is_ok=False,
            the_code=None)

    def test_creds_update_failure_bad_http_response_code(self):
        """Validates async_creds_deleter's behavior when
        the update of credentials being deleted fail."""
        self._test_creds_update_failure(
            the_is_ok=True,
            the_code=httplib.INTERNAL_SERVER_ERROR)
