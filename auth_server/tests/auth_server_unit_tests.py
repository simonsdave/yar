"""This module contains unit tests for the auth server's auth_server module."""

import httplib
import logging
import os
import sys
import unittest
import uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httplib2
import mock
import tornado.httpserver
import tornado.httputil
import tornado.web

import yar_test_util

import auth_server

_logger = logging.getLogger(__name__)

class AuthServer(yar_test_util.Server):
    """Mock auth server."""

    def __init__(self, generate_debug_headers=False):
        """Creates an instance of the auth server and starts the
        server listenting on a random, available port."""
        yar_test_util.Server.__init__(self)

        auth_server.generate_debug_headers = generate_debug_headers

        http_server = tornado.httpserver.HTTPServer(auth_server._app)
        http_server.add_sockets([self.socket])

class TestCase(yar_test_util.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.io_loop = yar_test_util.IOLoop()
        cls.io_loop.start()
        cls.auth_server = AuthServer()

    @classmethod
    def tearDownClass(cls):
        # :TODO: is this shutdown sequence right? shouldn't it be the
        # reverse of the startup sequence?
        cls.io_loop.stop()
        cls.io_loop = None
        cls.auth_server.shutdown()
        cls.auth_server = None

    def setUp(self):
        yar_test_util.TestCase.setUp(self)

    def tearDown(self):
        yar_test_util.TestCase.tearDown(self)

    def test_hmac_auth_failed(self):
        def validate_patch(an_async_hmac_auth, callback):
            self.assertIsNotNone(an_async_hmac_auth)
            self.assertIsNotNone(callback)
            callback(False)

        with mock.patch("async_hmac_auth.AsyncHMACAuth.validate", validate_patch):
            http_client = httplib2.Http()
            response, content = http_client.request(
                "http://localhost:%d/whatever" % self.__class__.auth_server.port,
                "GET")
            self.assertIsNotNone(response)
            self.assertIsNotNone(response.status)
            self.assertEqual(response.status, httplib.UNAUTHORIZED)

    def test_forward_to_app_server_failed(self):
        the_owner = str(uuid.uuid4()).replace("-", "")
        the_identifier = str(uuid.uuid4()).replace("-", "")

        def validate_patch(ignore_this_async_hmac_auth, callback):
            self.assertIsNotNone(callback)
            callback(True, owner=the_owner, identifier=the_identifier)

        with mock.patch("async_hmac_auth.AsyncHMACAuth.validate", validate_patch):
            def forward_patch(
                ignore_this_async_app_server_forwarder,
                method,
                uri,
                headers,
                body,
                owner,
                identifier,
                callback):

                self.assertIsNotNone(owner)
                self.assertEqual(owner, the_owner)

                self.assertIsNotNone(identifier)
                self.assertEqual(identifier, the_identifier)

                callback(False)

            with mock.patch("async_app_server_forwarder.AsyncAppServerForwarder.forward", forward_patch):
                http_client = httplib2.Http()
                response, content = http_client.request(
                    "http://localhost:%d/whatever" % self.__class__.auth_server.port,
                    "GET")
                self.assertIsNotNone(response)
                self.assertEqual(response.status, httplib.INTERNAL_SERVER_ERROR)
