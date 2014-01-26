"""This module implements unit tests for the key server's
async_creds_creator module."""

import httplib
import os
import sys
import uuid

import mock

from yar.key_server import async_creds_creator
from yar.key_server import ks_util
from yar import mac
from yar.tests import yar_test_util


class TestCaseAsyncCredsCreator(yar_test_util.TestCase):
    """A collection of unit tests for the key server's
    async_creds_creator module."""

    _key_store = "dave:42"

    def _test_bad(self, the_is_ok, the_auth_scheme, the_http_status_code):

        self.the_owner = str(uuid.uuid4()).replace("-", "")

        def async_req_to_key_store_patch(
            acc,
            path,
            method,
            body,
            callback):

            self.assertIsNotNone(acc)

            self.assertIsNotNone(path)

            self.assertIsNotNone(method)
            self.assertEqual(method, "PUT")

            self.assertIsNotNone(body)

            self.assertIn("owner", body)
            self.assertEqual(body["owner"], self.the_owner)

            self.assertIn("type", body)
            self.assertEqual(body["type"], "creds_v1.0")

            self.assertIn("is_deleted", body)
            self.assertFalse(body["is_deleted"])

            if the_auth_scheme == "hmac":
                self.assertIn("mac_key_identifier", body)
                self.assertEqual(body["mac_key_identifier"], path)

                self.assertIn("mac_key", body)

                self.assertIn("mac_algorithm", body)
                self.assertIn(body["mac_algorithm"], mac.MAC.algorithm)
            else:
                self.assertIn("api_key", body)

            self.assertIsNotNone(callback)
            callback(is_ok=the_is_ok, code=the_http_status_code)

        def on_async_create_done(creds):
            self.assertIsNone(creds)

        name_of_method_to_patch = (
            "yar.key_server.ks_util."
            "AsyncAction.async_req_to_key_store"
        )
        with mock.patch(name_of_method_to_patch, async_req_to_key_store_patch):
            acc = async_creds_creator.AsyncCredsCreator(type(self)._key_store)
            acc.create(
                self.the_owner,
                the_auth_scheme,
                on_async_create_done)

    def test_hmac_bad_is_ok(self):
        self._test_bad(
            the_is_ok=False,
            the_auth_scheme="hmac",
            the_http_status_code=httplib.CREATED)

    def test_hmac_bad_http_status_code(self):
        self._test_bad(
            the_is_ok=True,
            the_auth_scheme="hmac",
            the_http_status_code=httplib.BAD_REQUEST)

    def test_basic_bad_is_ok(self):
        self._test_bad(
            the_is_ok=False,
            the_auth_scheme="basic",
            the_http_status_code=httplib.CREATED)

    def test_basic_bad_http_status_code(self):
        self._test_bad(
            the_is_ok=True,
            the_auth_scheme="basic",
            the_http_status_code=httplib.BAD_REQUEST)

    def test_ok(self):

        self.the_owner = str(uuid.uuid4()).replace("-", "")
        self.the_creds = None

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
            self.the_creds = creds

            self.assertIn("owner", creds)
            self.assertEqual(creds["owner"], self.the_owner)

            self.assertIn("mac_key_identifier", creds)
            self.assertEqual(creds["mac_key_identifier"], mac_key_identifier)

            self.assertIn("mac_key", creds)

            self.assertIn("mac_algorithm", creds)
            self.assertIn(creds["mac_algorithm"], mac.MAC.algorithm)

            self.assertIn("type", creds)
            self.assertEqual(creds["type"], "creds_v1.0")

            self.assertIn("is_deleted", creds)
            self.assertFalse(creds["is_deleted"])

            self.assertIsNotNone(callback)
            callback(
                is_ok=True,
                code=httplib.CREATED,
                body=creds)

        def on_async_create_done(creds):
            self.assertIsNotNone(creds)
            self.assertIsNotNone(self.the_creds)
            self.assertEqual(
                creds,
                ks_util.filter_out_non_model_creds_properties(self.the_creds))

        name_of_method_to_patch = (
            "yar.key_server.ks_util."
            "AsyncAction.async_req_to_key_store"
        )
        with mock.patch(name_of_method_to_patch, async_req_to_key_store_patch):
            acc = async_creds_creator.AsyncCredsCreator(type(self)._key_store)
            acc.create(
                self.the_owner,
                "hmac",
                on_async_create_done)
