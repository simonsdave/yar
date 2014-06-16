"""This module implements unit tests for the key service's
async_creds_creator module."""

import httplib
import os
import sys
import uuid

import mock

from yar.key_service import async_creds_creator
from yar.key_service import ks_util
from yar.util import mac
from yar.tests import yar_test_util


class TestCaseAsyncCredsCreator(yar_test_util.TestCase):
    """A collection of unit tests for the key service's
    async_creds_creator module."""

    _key_store = "dave:42"

    def _test_bad(self, the_is_ok, the_auth_scheme, the_http_status_code):

        self.the_principal = uuid.uuid4().hex

        def async_req_to_key_store_patch(
            acc,
            path,
            method,
            body,
            callback):

            self.assertIsNotNone(acc)

            self.assertIsNotNone(path)
            self.assertEqual(path, "")

            self.assertIsNotNone(method)
            self.assertEqual(method, "POST")

            self.assertIsNotNone(body)

            self.assertIn("principal", body)
            self.assertEqual(body["principal"], self.the_principal)

            self.assertIn("type", body)
            self.assertEqual(body["type"], "creds_v1.0")

            if the_auth_scheme == "mac":
                self.assertIn("mac", body)
                mac_section_of_body = body["mac"]

                self.assertIn("mac_key_identifier", mac_section_of_body)

                self.assertIn("mac_key", mac_section_of_body)

                self.assertIn("mac_algorithm", mac_section_of_body)
                self.assertEqual(
                    mac_section_of_body["mac_algorithm"],
                    mac.MAC.algorithm)
            else:
                self.assertIn("basic", body)
                basic_section_of_body = body["basic"]

                self.assertIn("api_key", basic_section_of_body)

            self.assertIsNotNone(callback)
            callback(is_ok=the_is_ok, code=the_http_status_code)

        def on_async_create_done(creds):
            self.assertIsNone(creds)

        name_of_method_to_patch = (
            "yar.key_service.ks_util."
            "AsyncAction.async_req_to_key_store"
        )
        with mock.patch(name_of_method_to_patch, async_req_to_key_store_patch):
            acc = async_creds_creator.AsyncCredsCreator(type(self)._key_store)
            acc.create(
                self.the_principal,
                the_auth_scheme,
                on_async_create_done)

    def test_mac_bad_is_ok(self):
        self._test_bad(
            the_is_ok=False,
            the_auth_scheme="mac",
            the_http_status_code=httplib.CREATED)

    def test_mac_bad_http_status_code(self):
        self._test_bad(
            the_is_ok=True,
            the_auth_scheme="mac",
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

    def _test_ok(self, the_auth_scheme):

        self.the_principal = uuid.uuid4().hex
        self.the_creds = None

        def async_req_to_key_store_patch(
            acc,
            path,
            method,
            body,
            callback):

            self.assertIsNotNone(acc)

            self.assertIsNotNone(path)
            self.assertEqual(path, "")

            self.assertIsNotNone(method)
            self.assertEqual(method, "POST")

            self.assertIsNotNone(body)
            self.the_creds = body

            self.assertIn("principal", body)
            self.assertEqual(body["principal"], self.the_principal)

            self.assertIn("type", body)
            self.assertEqual(body["type"], "creds_v1.0")

            if the_auth_scheme == "mac":
                self.assertIn("mac", body)
                mac_section_of_body = body["mac"]

                self.assertIn("mac_key_identifier", mac_section_of_body)

                self.assertIn("mac_key", mac_section_of_body)

                self.assertIn("mac_algorithm", mac_section_of_body)
                self.assertEqual(
                    mac_section_of_body["mac_algorithm"],
                    mac.MAC.algorithm)
            else:
                self.assertIn("basic", body)
                basic_section_of_body = body["basic"]

                self.assertIn("api_key", basic_section_of_body)

            self.assertIsNotNone(callback)
            callback(is_ok=True, code=httplib.CREATED, body=body)

        def on_async_create_done(creds):
            self.assertIsNotNone(creds)
            self.assertIsNotNone(self.the_creds)
            self.assertEqual(
                creds,
                ks_util.filter_out_non_model_creds_properties(self.the_creds))

        name_of_method_to_patch = (
            "yar.key_service.ks_util."
            "AsyncAction.async_req_to_key_store"
        )
        with mock.patch(name_of_method_to_patch, async_req_to_key_store_patch):
            acc = async_creds_creator.AsyncCredsCreator(type(self)._key_store)
            acc.create(
                self.the_principal,
                the_auth_scheme,
                on_async_create_done)

    def test_mac_ok(self):
        self._test_ok("mac")

    def test_basic_ok(self):
        self._test_ok("basic")
