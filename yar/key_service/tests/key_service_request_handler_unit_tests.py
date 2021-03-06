"""This module implements the key service's unit tests."""

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

from yar.key_service import jsonschemas
from yar.key_service import key_service_request_handler
from yar.util import mac
from yar.util import basic
from yar.tests import yar_test_util


class KeyServer(yar_test_util.Server):

    def __init__(self, key_store):
        yar_test_util.Server.__init__(self)

        key_service_request_handler._key_store = key_store

        handlers = [
            (
                key_service_request_handler.url_spec,
                key_service_request_handler.RequestHandler
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
        cls._key_service = KeyServer("127.0.0.1:5984/%s" % cls._database_name)
        cls._ioloop = yar_test_util.IOLoop()
        cls._ioloop.start()

    @classmethod
    def tearDownClass(cls):
        cls._ioloop.stop()
        cls._key_service.shutdown()
        cls._key_service = None
        cls._database_name = None

    def setUp(self):
        self._creds_database = []

    def url(self):
        return "http://127.0.0.1:%s/v1.0/creds" % type(self)._key_service.port

    def _key_from_creds(self, creds):
        if "mac" in creds:
            key = creds["mac"].get("mac_key_identifier", None)
        else:
            key = creds["basic"].get("api_key", None)
        return key

    def _create_creds(self, the_principal, the_auth_scheme="mac"):
        self.assertIsNotNone(the_principal)
        self.assertTrue(0 < len(the_principal))

        def create_patch(acc, principal, auth_scheme, callback):
            self.assertIsNotNone(acc)
            self.assertEqual(principal, the_principal)
            self.assertEqual(auth_scheme, the_auth_scheme)
            self.assertIsNotNone(callback)

            creds = {
                "principal": principal,
            }
            if auth_scheme == "mac":
                creds["mac"] = {
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
            "yar.key_service.async_creds_creator."
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

    def _get_creds(self, the_key, expected_to_be_found=True):

        self.assertIsNotNone(the_key)
        self.assertTrue(0 < len(the_key))

        def fetch_patch(acr,
                        callback,
                        key,
                        principal,
                        is_filter_out_non_model_properties):

            self.assertIsNotNone(acr)
            self.assertIsNotNone(callback)
            self.assertIsNotNone(key)
            self.assertEqual(key, the_key)
            self.assertIsNone(principal)

            for creds in self._creds_database:
                key = self._key_from_creds(creds)
                if the_key == key:
                    callback(creds=creds, is_creds_collection=False)
                    return
            callback(creds=None, is_creds_collection=None)

        name_of_method_to_patch = (
            "yar.key_service.async_creds_retriever."
            "AsyncCredsRetriever.fetch"
        )
        with mock.patch(name_of_method_to_patch, fetch_patch):
            url = "%s/%s" % (self.url(), the_key)
            http_client = httplib2.Http()
            response, content = http_client.request(url, "GET")
            if not expected_to_be_found:
                self.assertTrue(httplib.NOT_FOUND == response.status)
                return None
            self.assertEqual(httplib.OK, response.status)

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

    def _get_all_creds(self, the_principal):

        self.assertIsNotNone(the_principal)
        self.assertTrue(0 < len(the_principal))

        def fetch_patch(acr,
                        callback,
                        key,
                        principal,
                        is_filter_out_non_model_properties):

            self.assertIsNotNone(acr)
            self.assertIsNotNone(callback)
            self.assertIsNone(key)
            if the_principal is None:
                self.assertIsNone(principal)
            else:
                self.assertEqual(principal, the_principal)
            if principal is None:
                callback(creds=self._creds_database, is_creds_collection=True)
            else:
                principals_creds = []
                for creds in self._creds_database:
                    self.assertIn("principal", creds)
                    if principal == creds["principal"]:
                        principals_creds.append(creds)
                callback(creds=principals_creds, is_creds_collection=True)

        name_of_method_to_patch = (
            "yar.key_service.async_creds_retriever."
            "AsyncCredsRetriever.fetch"
        )
        with mock.patch(name_of_method_to_patch, fetch_patch):
            url = "%s?principal=%s" % (self.url(), the_principal)
            http_client = httplib2.Http()
            response, content = http_client.request(url, "GET")
            self.assertIsNotNone(response)
            self.assertEqual(httplib.OK, response.status)
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

        def async_creds_deleter_patch(acd, key, callback):
            self.assertIsNotNone(acd)
            self.assertIsNotNone(key)
            self.assertEqual(key, the_key)
            self.assertIsNotNone(callback)
            new_creds_database = [creds for creds in self._creds_database if key != self._key_from_creds(creds)]
            deleted = len(new_creds_database) != len(self._creds_database)
            self._creds_database = new_creds_database
            callback(deleted)

        name_of_method_to_patch = (
            "yar.key_service.async_creds_deleter."
            "AsyncCredsDeleter.delete"
        )
        with mock.patch(name_of_method_to_patch, async_creds_deleter_patch):
            url = "%s/%s" % (self.url(), the_key)
            http_client = httplib2.Http()
            response, content = http_client.request(url, "DELETE")
            self.assertTrue(httplib.OK == response.status)

    def test_get_of_non_existent_resource(self):
        the_key = uuid.uuid4().hex

        def fetch_patch(acr,
                        callback,
                        key,
                        principal,
                        is_filter_out_non_model_properties):
            self.assertIsNotNone(acr)
            self.assertIsNotNone(callback)
            self.assertEqual(key, the_key)
            callback(creds=None, is_creds_collection=None)

        name_of_method_to_patch = (
            "yar.key_service.async_creds_retriever."
            "AsyncCredsRetriever.fetch"
        )
        with mock.patch(name_of_method_to_patch, fetch_patch):
            url = "%s/%s" % (self.url(), the_key)
            http_client = httplib2.Http()
            response, content = http_client.request(url, "GET")
            self.assertIsNotNone(response)
            self.assertTrue(httplib.NOT_FOUND == response.status)

    def test_get_with_no_principal_and_no_key(self):
        http_client = httplib2.Http()
        response, content = http_client.request(self.url(), "GET")
        self.assertIsNotNone(response)
        self.assertTrue(httplib.BAD_REQUEST == response.status)

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
        the_principal = uuid.uuid4().hex

        def create_patch(acc, principal, callback):
            self.assertIsNotNone(acc)
            self.assertEqual(principal, the_principal)
            self.assertIsNotNone(callback)
            callback(None)

        with mock.patch("yar.key_service.async_creds_creator.AsyncCredsCreator.create", create_patch):
            http_client = httplib2.Http()
            response, content = http_client.request(
                self.url(),
                "POST",
                body=json.dumps({"principal": the_principal}),
                headers={"Content-Type": "application/json; charset=utf8"})
            self.assertIsNotNone(response)
            self.assertTrue(httplib.INTERNAL_SERVER_ERROR == response.status)

    def test_delete_failure(self):
        the_mac_key_identifier = uuid.uuid4().hex

        def delete_patch(acd, mac_key_identifier, callback):
            self.assertIsNotNone(acd)
            self.assertIsNotNone(mac_key_identifier)
            self.assertEqual(mac_key_identifier, the_mac_key_identifier)
            self.assertIsNotNone(callback)
            callback(None)

        name_of_method_to_patch = (
            "yar.key_service.async_creds_deleter."
            "AsyncCredsDeleter.delete"
        )
        with mock.patch(name_of_method_to_patch, delete_patch):
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
        principal = uuid.uuid4().hex
        principal_creds = []
        for x in range(1, 11):
            principal_creds.append(self._create_creds(principal))

        other_principal = uuid.uuid4().hex
        other_principal_creds = []
        for x in range(1, 4):
            other_principal_creds.append(self._create_creds(other_principal))

        all_principal_creds = self._get_all_creds(principal)
        self.assertIsNotNone(all_principal_creds)
        self.assertEqual(len(all_principal_creds), len(principal_creds))
        # :TODO: validate all_principal_creds is same as principal_creds

    def _test_all_good_for_simple_create_and_delete(self, auth_scheme):
        principal = uuid.uuid4().hex
        (creds, location) = self._create_creds(principal, auth_scheme)
        self.assertIsNotNone(creds)

        key = self._key_from_creds(creds)
        self.assertIsNotNone(key)
        self.assertTrue(0 < len(key))

        self._delete_creds(key)
        # :TODO:self._delete_creds(key)

        all_creds = self._get_all_creds(principal)
        self.assertIsNotNone(all_creds)
        self.assertEqual(0, len(all_creds))

    def test_all_good_for_simple_create_and_delete_mac(self):
        self._test_all_good_for_simple_create_and_delete("mac")

    def test_all_good_for_simple_create_and_delete_basic(self):
        self._test_all_good_for_simple_create_and_delete("basic")

    def test_deleted_creds_not_returned_by_default_on_get(self):
        principal = uuid.uuid4().hex
        (creds_on_create, location_on_create) = self._create_creds(principal)
        key = self._key_from_creds(creds_on_create)
        creds_on_get_before_delete = self._get_creds(key)
        self.assertIsNotNone(creds_on_get_before_delete)
        self._delete_creds(key)
        self._get_creds(key, expected_to_be_found=False)

    def test_create_creds_failure(self):
        """Verify that when credentials creation fails (for whatever reason)
        that the key service returns an INTERNAL_SERVER_ERROR status code."""

        def create_patch(acc, principal, auth_scheme, callback):
            # the "None" below indicates a failure has occured
            callback(None)

        name_of_method_to_patch = (
            "yar.key_service.async_creds_creator."
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
