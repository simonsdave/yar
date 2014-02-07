"""This module implements the key server's unit tests."""

import httplib
import httplib2
import json
import logging
import re
import os
import socket
import sys
import time
import unittest
import uuid

import mock
import jsonschema
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.options
import tornado.web

from yar.key_server import jsonschemas
from yar.key_server import key_server_request_handler
from yar.util import mac
from yar.util import basic
from yar.tests import yar_test_util


class KeyServer(yar_test_util.Server):

    def __init__(self, key_store):
        yar_test_util.Server.__init__(self)

        key_server_request_handler._key_store = key_store

        handlers = [
            (
                key_server_request_handler.url_spec,
                key_server_request_handler.RequestHandler
            ),
        ]
        app = tornado.web.Application(handlers=handlers)

        http_server = tornado.httpserver.HTTPServer(app)
        http_server.add_sockets([self.socket])


class TestCase(yar_test_util.TestCase):

    _database_name = None

    @classmethod
    def setUpClass(cls):
        cls._database_name = "das%s" % str(uuid.uuid4()).replace("-", "")[:7]
        cls._key_server = KeyServer("127.0.0.1:5984/%s" % cls._database_name)
        cls._ioloop = yar_test_util.IOLoop()
        cls._ioloop.start()

    @classmethod
    def tearDownClass(cls):
        cls._ioloop.stop()
        cls._key_server.shutdown()
        cls._key_server = None
        cls._database_name = None

    def setUp(self):
        self._creds_database = []

    def url(self):
        return "http://127.0.0.1:%s/v1.0/creds" % self.__class__._key_server.port

    def _key_from_creds(self, creds):
        if "hmac" in creds:
            key = creds["hmac"].get("mac_key_identifier", None)
        else:
            key = creds["basic"].get("api_key", None)
        return key

    def _create_creds(self, the_principal, the_auth_scheme="hmac"):
        self.assertIsNotNone(the_principal)
        self.assertTrue(0 < len(the_principal))

        def create_patch(acc, principal, auth_scheme, callback):
            self.assertIsNotNone(acc)
            self.assertEqual(principal, the_principal)
            self.assertEqual(auth_scheme, the_auth_scheme)
            self.assertIsNotNone(callback)

            creds = {
                "principal": principal,
                "is_deleted": False,
            }
            if auth_scheme == "hmac":
                creds["hmac"] = {
                    "mac_key_identifier": mac.MACKeyIdentifier.generate(),
                    "mac_key": mac.MACKey.generate(),
                    "mac_algorithm": mac.MAC.algorithm,
                }
            else:
                creds["basic"] = {
                    "api_key": basic.APIKey.generate(),
                }

            callback(creds)

        name_of_method_to_patch = (
            "yar.key_server.async_creds_creator."
            "AsyncCredsCreator.create"
        )
        with mock.patch(name_of_method_to_patch, create_patch):
            http_client = httplib2.Http()
            body = {
                "principal": the_principal,
                "auth_scheme": the_auth_scheme,
            }
            body_as_json = json.dumps(body)
            headers = {
                "Content-type": "application/json; charset=utf8",
                "Content-length": str(len(body_as_json)),
            }
            response, content = http_client.request(
                self.url(),
                "POST",
                body=body_as_json,
                headers=headers)
            self.assertIsNotNone(response)
            self.assertTrue(httplib.CREATED == response.status)

            self.assertTrue("content-type" in response)
            content_type = response["content-type"]
            self.assertIsJsonUtf8ContentType(content_type)

            self.assertIsNotNone(content)
            creds = json.loads(content)
            self.assertIsNotNone(creds)
            jsonschema.validate(
                creds,
                jsonschemas.create_creds_response)

            self.assertEqual(the_principal, creds.get("principal", None))

            key = self._key_from_creds(creds)
            self.assertIsNotNone(key)

            self.assertTrue("location" in response)
            location = response["location"]
            self.assertIsNotNone(location)
            expected_location = "%s/%s" % (self.url(), key)
            self.assertEqual(location, expected_location)

            self.assertEqual(
                location,
                creds["links"]["self"]["href"])

            self._creds_database.append(creds)

            return (creds, location)

    def _get_creds(
        self,
        the_key,
        expected_to_be_found=True,
        get_deleted=False):

        self.assertIsNotNone(the_key)
        self.assertTrue(0 < len(the_key))

        def fetch_patch(
            acr,
            callback,
            key,
            principal,
            is_filter_out_deleted,
            is_filter_out_non_model_properties):

            self.assertIsNotNone(acr)
            self.assertIsNotNone(callback)
            self.assertIsNotNone(key)
            self.assertEqual(key, the_key)
            self.assertIsNone(principal)

            for creds in self._creds_database:
                key = self._key_from_creds(creds)
                if the_key == key:
                    if is_filter_out_deleted:
                        self.assertIn("is_deleted", creds)
                        if creds["is_deleted"]:
                            callback(creds=None, is_creds_collection=False)
                            return
                    callback(creds=creds, is_creds_collection=False)
                    return
            callback(creds=None, is_creds_collection=None)

        name_of_method_to_patch = (
            "yar.key_server.async_creds_retriever.AsyncCredsRetriever.fetch"
        )
        with mock.patch(name_of_method_to_patch, fetch_patch):
            url = "%s/%s" % (self.url(), the_key)
            if get_deleted:
                url = "%s?deleted=true" % url
            http_client = httplib2.Http()
            response, content = http_client.request(url, "GET")
            if not expected_to_be_found:
                self.assertTrue(httplib.NOT_FOUND == response.status)
                return None
            self.assertTrue(httplib.OK == response.status)

            self.assertTrue("content-type" in response)
            content_type = response["content-type"]
            self.assertIsJsonUtf8ContentType(content_type)

            creds = json.loads(content)
            self.assertIsNotNone(creds)
            jsonschema.validate(
                creds,
                jsonschemas.get_creds_response)

            key = self._key_from_creds(creds)
            self.assertIsNotNone(key)
            self.assertEqual(the_key, key)

            print type(response)
            print url
            print response
            self.assertTrue("location" in response)
            location = response["location"]
            self.assertIsNotNone(location)
            expected_location = "%s/%s" % (self.url(), key)
            self.assertEqual(location, expected_location)

            self.assertEqual(
                location,
                creds["links"]["self"]["href"])

            return creds

    def _get_all_creds(self, the_principal=None):

        def fetch_patch(
            acr,
            callback,
            key,
            principal,
            is_filter_out_deleted,
            is_filter_out_non_model_properties):

            self.assertIsNotNone(acr)
            self.assertIsNotNone(callback)
            self.assertIsNone(key)
            if the_principal is None:
                self.assertIsNone(principal)
            else:
                self.assertEqual(principal, the_principal)
            if is_filter_out_deleted:
                creds_database = [creds for creds in self._creds_database if not creds.get("is_deleted", False)]
            else:
                creds_database = self._creds_database
            if principal is None:
                callback(creds=creds_database, is_creds_collection=True)
            else:
                principals_creds = []
                for creds in creds_database:
                    self.assertIn("principal", creds)
                    if principal == creds["principal"]:
                        principals_creds.append(creds)
                callback(creds=principals_creds, is_creds_collection=True)

        name_of_method_to_patch = (
            "yar.key_server.async_creds_retriever."
            "AsyncCredsRetriever.fetch"
        )
        with mock.patch(name_of_method_to_patch, fetch_patch):
            http_client = httplib2.Http()
            url = self.url()
            if the_principal is not None:
                self.assertTrue(0 < len(the_principal))
                url = "%s?principal=%s" % (url, the_principal)
            response, content = http_client.request(url, "GET")
            self.assertIsNotNone(response)
            self.assertTrue(httplib.OK == response.status)
            self.assertTrue("content-type" in response)
            content_type = response["content-type"]
            self.assertIsJsonUtf8ContentType(content_type)
            self.assertTrue("content-length" in response)
            content_length = response["content-length"]
            content_length = int(content_length)
            self.assertTrue(0 < content_length)
            self.assertIsNotNone(content)
            self.assertTrue(0 < len(content))
            self.assertEqual(content_length, len(content))
            creds = json.loads(content)
            self.assertIsNotNone(creds)
            self.assertTrue("creds" in creds)
            return creds["creds"]

    def _delete_creds(self, the_key):
        self.assertIsNotNone(the_key)
        self.assertTrue(0 < len(the_key))

        def delete_patch(acd, key, callback):
            self.assertIsNotNone(acd)
            self.assertIsNotNone(key)
            self.assertEqual(key, the_key)
            self.assertIsNotNone(callback)
            for creds in self._creds_database:
                if key == self._key_from_creds(creds):
                    creds["is_deleted"] = True
                    callback(True)
                    return
            callback(False)

        name_of_method_to_patch = (
            "yar.key_server.async_creds_deleter.AsyncCredsDeleter.delete"
        )
        with mock.patch(name_of_method_to_patch, delete_patch):
            url = "%s/%s" % (self.url(), the_key)
            http_client = httplib2.Http()
            response, content = http_client.request(url, "DELETE")
            self.assertTrue(httplib.OK == response.status)

    def test_get_of_non_existent_resource(self):
        the_key = str(uuid.uuid4()).replace("-", "")

        def fetch_patch(
            acr,
            callback,
            key,
            principal,
            is_filter_out_deleted,
            is_filter_out_non_model_properties):
            self.assertIsNotNone(acr)
            self.assertIsNotNone(callback)
            self.assertEqual(key, the_key)
            callback(creds=None, is_creds_collection=None)

        name_of_method_to_patch = (
            "yar.key_server.async_creds_retriever."
            "AsyncCredsRetriever.fetch"
        )
        with mock.patch(name_of_method_to_patch, fetch_patch):
            url = "%s/%s" % (self.url(), the_key)
            http_client = httplib2.Http()
            response, content = http_client.request(url, "GET")
            self.assertIsNotNone(response)
            self.assertTrue(httplib.NOT_FOUND == response.status)

    def test_post_with_no_content_type_header(self):
        http_client = httplib2.Http()
        response, content = http_client.request(
            self.url(),
            "POST",
            body=json.dumps({"principal": "simonsdave@gmail.com"}),
            headers={})
        self.assertIsNotNone(response)
        self.assertTrue(httplib.BAD_REQUEST == response.status)

    def test_post_with_unsupported_content_type_header(self):
        http_client = httplib2.Http()
        response, content = http_client.request(
            self.url(),
            "POST",
            body=json.dumps({"principal": "simonsdave@gmail.com"}),
            headers={"Content-Type": "text/plain"})
        self.assertIsNotNone(response)
        self.assertTrue(httplib.BAD_REQUEST == response.status)

    def test_post_with_no_body(self):
        http_client = httplib2.Http()
        response, content = http_client.request(
            self.url(),
            "POST",
            headers={"Content-Type": "application/json; charset=utf8"})
        self.assertIsNotNone(response)
        self.assertTrue(httplib.BAD_REQUEST == response.status)

    def test_post_with_zero_length_body(self):
        http_client = httplib2.Http()
        response, content = http_client.request(
            self.url(),
            "POST",
            body="",
            headers={"Content-Type": "application/json; charset=utf8"})
        self.assertIsNotNone(response)
        self.assertTrue(httplib.BAD_REQUEST == response.status)

    def test_post_with_non_json_body(self):
        http_client = httplib2.Http()
        response, content = http_client.request(
            self.url(),
            "POST",
            body="dave_was_here",
            headers={"Content-Type": "application/json; charset=utf8"})
        self.assertIsNotNone(response)
        self.assertTrue(httplib.BAD_REQUEST == response.status)

    def test_post_with_no_principal_in_body(self):
        http_client = httplib2.Http()
        response, content = http_client.request(
            self.url(),
            "POST",
            body=json.dumps({"XXXprincipalXXX": "simonsdave@gmail.com"}),
            headers={"Content-Type": "application/json; charset=utf8"})
        self.assertIsNotNone(response)
        self.assertTrue(httplib.BAD_REQUEST == response.status)

    def test_post_failure(self):
        the_principal = str(uuid.uuid4()).replace("-", "")

        def create_patch(acc, principal, callback):
            self.assertIsNotNone(acc)
            self.assertEqual(principal, the_principal)
            self.assertIsNotNone(callback)
            callback(None)

        with mock.patch("yar.key_server.async_creds_creator.AsyncCredsCreator.create", create_patch):
            http_client = httplib2.Http()
            response, content = http_client.request(
                self.url(),
                "POST",
                body=json.dumps({"principal": the_principal}),
                headers={"Content-Type": "application/json; charset=utf8"})
            self.assertIsNotNone(response)
            self.assertTrue(httplib.INTERNAL_SERVER_ERROR == response.status)

    def test_delete_failure(self):
        the_mac_key_identifier = str(uuid.uuid4()).replace("-", "")

        def delete_patch(acd, mac_key_identifier, callback):
            self.assertIsNotNone(acd)
            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)
            self.assertIsNotNone(callback)
            callback(None)

        with mock.patch("yar.key_server.async_creds_deleter.AsyncCredsDeleter.delete", delete_patch):
            url = "%s/%s" % (self.url(), the_mac_key_identifier)
            http_client = httplib2.Http()
            response, content = http_client.request(url, "DELETE")
            self.assertIsNotNone(response)
            self.assertTrue(httplib.INTERNAL_SERVER_ERROR == response.status)

    def test_delete_method_on_creds_collection_resource(self):
        http_client = httplib2.Http()
        response, content = http_client.request(self.url(), "DELETE")
        self.assertIsNotNone(response)
        self.assertTrue(httplib.METHOD_NOT_ALLOWED == response.status)

    def test_put_method_on_creds_collection_resource(self):
        http_client = httplib2.Http()
        response, content = http_client.request(self.url(), "PUT")
        self.assertIsNotNone(response)
        self.assertTrue(httplib.METHOD_NOT_ALLOWED == response.status)

    def test_post_method_on_creds_resource(self):
        http_client = httplib2.Http()
        url = "%s/%s" % (self.url(), "dave")
        response, content = http_client.request(url, "POST")
        self.assertIsNotNone(response)
        self.assertTrue(httplib.METHOD_NOT_ALLOWED == response.status)

    def test_put_method_on_creds_resource(self):
        http_client = httplib2.Http()
        url = "%s/%s" % (self.url(), "dave")
        response, content = http_client.request(url, "PUT")
        self.assertIsNotNone(response)
        self.assertTrue(httplib.METHOD_NOT_ALLOWED == response.status)

    def test_get_by_principal(self):
        principal = str(uuid.uuid4()).replace("-", "")
        principal_creds = []
        for x in range(1, 11):
            principal_creds.append(self._create_creds(principal))

        other_principal = str(uuid.uuid4()).replace("-", "")
        other_principal_creds = []
        for x in range(1, 4):
            other_principal_creds.append(self._create_creds(other_principal))

        all_principal_creds = self._get_all_creds(principal)
        self.assertIsNotNone(all_principal_creds)
        self.assertEqual(len(all_principal_creds), len(principal_creds))
        # :TODO: validate all_principal_creds is same as principal_creds

    def _test_all_good_for_simple_create_and_delete(self, auth_scheme):
        all_creds = self._get_all_creds()
        self.assertIsNotNone(all_creds)
        self.assertEqual(0, len(all_creds))

        principal = str(uuid.uuid4()).replace("-", "")
        (creds, location) = self._create_creds(principal, auth_scheme)
        self.assertIsNotNone(creds)

        key = self._key_from_creds(creds)
        self.assertIsNotNone(key)
        self.assertTrue(0 < len(key))

        self._delete_creds(key)
        # self._delete_creds(key)

        all_creds = self._get_all_creds()
        self.assertIsNotNone(all_creds)
        self.assertEqual(0, len(all_creds))

    def test_all_good_for_simple_create_and_delete_hmac(self):
        self._test_all_good_for_simple_create_and_delete("hmac")

    def test_all_good_for_simple_create_and_delete_basic(self):
        self._test_all_good_for_simple_create_and_delete("basic")

    def test_deleted_creds_not_returned_by_default_on_get(self):
        principal = str(uuid.uuid4()).replace("-", "")
        (creds_on_create, location_on_create) = self._create_creds(principal)
        key = self._key_from_creds(creds_on_create)
        creds_on_get_before_delete = self._get_creds(key)
        self.assertIsNotNone(creds_on_get_before_delete)
        self._delete_creds(key)
        self._get_creds(key, expected_to_be_found=False)
        self._get_creds(key, get_deleted=True)

    def test_create_creds_failure(self):
        """Verify that when credentials creation fails (for whatever reason)
        that the key server returns an INTERNAL_SERVER_ERROR status code."""

        def create_patch(acc, principal, auth_scheme, callback):
            # the "None" below indicates a failure has occured
            callback(None)

        name_of_method_to_patch = (
            "yar.key_server.async_creds_creator."
            "AsyncCredsCreator.create"
        )
        with mock.patch(name_of_method_to_patch, create_patch):
            http_client = httplib2.Http()
            body = {
                "principal": str(uuid.uuid4()).replace("-", ""),
                "auth_scheme": "basic",
            }
            body_as_json = json.dumps(body)
            headers = {
                "Content-type": "application/json; charset=utf8",
                "Content-length": str(len(body_as_json)),
            }
            response, content = http_client.request(
                self.url(),
                "POST",
                body=body_as_json,
                headers=headers)

            self.assertIsNotNone(response)
            self.assertEqual(httplib.INTERNAL_SERVER_ERROR, response.status)
