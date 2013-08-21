"""This module implements unit tests for the key server's
async_creds_creator module."""

import httplib
import os
import sys
import uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mock

import mac
import yar_test_util

import async_creds_creator

class TestCaseAsyncCredsCreator(yar_test_util.TestCase):
    """A collection of unit tests for the key server's
    async_creds_creator module."""

    _key_store = "dave:42"

    def _test_bad(self, the_is_ok, the_http_status_code):

        the_owner = str(uuid.uuid4()).replace("-", "")

        def async_req_to_key_store_patch(
            acc,
            mac_key_identifier,
            http_method,
            creds,
            callback):

            self.assertIsNotNone(acc)

            self.assertIsNotNone(mac_key_identifier)

            self.assertIsNotNone(http_method)
            self.assertEqual(http_method, "PUT")

            self.assertIsNotNone(creds)

            self.assertIn("owner", creds)
            self.assertEqual(creds["owner"], the_owner)

            self.assertIn("mac_key_identifier", creds)
            self.assertEqual(creds["mac_key_identifier"], mac_key_identifier)

            self.assertIn("mac_key", creds)

            self.assertIn("mac_algorithm", creds)
            self.assertIn(creds["mac_algorithm"], mac.MAC.algorithm)

            self.assertIn("type", creds)
            self.assertEqual(creds["type"], "cred_v1.0")

            self.assertIn("is_deleted", creds)
            self.assertFalse(creds["is_deleted"])

            self.assertIsNotNone(callback)
            callback(is_ok=the_is_ok, code=the_http_status_code)

        def on_async_create_done(is_ok):
            self.assertFalse(is_ok)

        name_of_method_to_patch = "ks_util.AsyncAction.async_req_to_key_store"
        with mock.patch(name_of_method_to_patch, async_req_to_key_store_patch):
            acc = async_creds_creator.AsyncCredsCreator(type(self)._key_store)
            acc.create(
                the_owner,
                on_async_create_done)

    def test_bad_is_ok(self):
        self._test_bad(the_is_ok=False, the_http_status_code=httplib.CREATED)

    def test_bad_http_status_code(self):
        self._test_bad(the_is_ok=True, the_http_status_code=httplib.BAD_REQUEST)
