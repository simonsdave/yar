"""This module contains the auth server's unit tests."""

import httplib
import httplib2
import json
import logging
import os
import re
import sys
import time
import uuid
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tornado.httpserver
import tornado.web

import async_creds_retriever
import async_nonce_checker
import auth_server
import mac
import testutil

_logger = logging.getLogger(__name__)


class KeyServerRequestHandler(tornado.web.RequestHandler):
    """Tornado request handler for use by the mock key server. This request
    handler only implements HTTP GET since that's the only type of request the
    auth server issues to the key server."""

    def get(self):
        """Implements HTTP GET for the mock key server."""
        _logger.info(
            "Mock Key Server GET %s",
            self.request.uri)
        uri_reg_ex = re.compile(
            '^/v1\.0/creds/(?P<mac_key_identifier>.+)$',
            re.IGNORECASE)
        match = uri_reg_ex.match(self.request.uri)
        if not match:
            TestCase._mac_key_identifier_in_key_server_request = None
            self.set_status(httplib.BAD_REQUEST)
        else:
            assert 0 == match.start()
            assert len(self.request.uri) == match.end()
            assert 1 == len(match.groups())
            mac_key_identifier = match.group("mac_key_identifier")
            assert mac_key_identifier is not None
            assert 0 < len(mac_key_identifier)

            TestCase._mac_key_identifier_in_key_server_request = \
                mac_key_identifier

            status = \
                TestCase.status_code_of_response_to_key_server_request \
                or \
                httplib.OK
            self.set_status(status)

            if status == httplib.OK:
                dict = TestCase.body_of_response_to_key_server_request \
                    or \
                    {
                        "is_deleted": False,
                        "mac_algorithm": TestCase.mac_algorithm_response_to_key_server_request,
                        "mac_key": TestCase.mac_key_in_response_to_key_server_request,
                        "mac_key_identifier": mac_key_identifier,
                        "owner": TestCase.owner_in_response_to_key_server_request or str(uuid.uuid4()),
                    }
                body = json.dumps(dict)
                self.write(body)

                self.set_header(
                    TestCase.content_type_of_response_to_key_server_request
                    or
                    "Content-Type", "application/json; charset=utf8")


class KeyServer(testutil.Server):
    """The mock key server."""

    def __init__(self):
        """Creates an instance of the mock key server and starts the
        server listenting on a random, available port."""
        testutil.Server.__init__(self)

        handlers = [(r".*", KeyServerRequestHandler)]
        app = tornado.web.Application(handlers=handlers)
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.add_sockets([self.socket])


class AuthenticationServer(testutil.Server):
    """Mock authentication server."""

    def __init__(self, nonce_store, key_server, app_server, app_server_auth_method):
        """Creates an instance of the auth server and starts the
        server listenting on a random, available port."""
        testutil.Server.__init__(self)

        async_creds_retriever.key_server = "localhost:%d" % key_server.port
        auth_server.app_server = "localhost:%d" % app_server.port
        auth_server.app_server_auth_method = app_server_auth_method
        auth_server.include_auth_failure_detail = True
        async_nonce_checker.nonce_store = nonce_store.memcached_cluster

        http_server = tornado.httpserver.HTTPServer(auth_server._app)
        http_server.add_sockets([self.socket])


class TestCase(testutil.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.io_loop = testutil.IOLoop()
        cls.io_loop.start()
        cls.asrs = testutil.AppServerRequestState()
        cls.app_server = testutil.AppServer(cls.asrs)
        cls.app_server_auth_method = str(uuid.uuid4()).replace("-", "")
        cls.key_server = KeyServer()
        cls.nonce_store = testutil.NonceStore()
        cls.auth_server = AuthenticationServer(
            cls.nonce_store,
            cls.key_server,
            cls.app_server,
            cls.app_server_auth_method)

    @classmethod
    def tearDownClass(cls):
        cls.io_loop.stop()
        cls.io_loop = None
        cls.auth_server.shutdown()
        cls.auth_server = None
        cls.nonce_store.shutdown()
        cls.nonce_store = None
        cls.key_server.shutdown()
        cls.key_server = None
        cls.app_server.shutdown()
        cls.app_server = None
        cls.asrs = None

    """When KeyServerRequestHandler's get() is given a valid
    mac key identifier, _mac_key_identifier_in_key_server_request
    is set to the mac key identifier in the handler.
    See TestCase's assertMACKeyIdentifierInKeyServerRequest()
    for when _mac_key_identifier_in_key_server_request is used."""
    _mac_key_identifier_in_key_server_request = None

    """..."""
    status_code_of_response_to_key_server_request = None

    """..."""
    content_type_of_response_to_key_server_request = None

    """..."""
    body_of_response_to_key_server_request = None

    """..."""
    mac_key_in_response_to_key_server_request = None

    """..."""
    mac_algorithm_response_to_key_server_request = None

    """When the mock key server responds to the auth server's request
    for credentials, ```owner_in_response_to_key_server_request```
    is used for the owner attribute."""
    owner_in_response_to_key_server_request = None

    def setUp(self):
        testutil.TestCase.setUp(self)
        self.__class__._mac_key_identifier_in_key_server_request = None
        self.__class__.status_code_of_response_to_key_server_request = None
        self.__class__.content_type_of_response_to_key_server_request = None
        self.__class__.body_of_response_to_key_server_request = None
        self.__class__.mac_key_in_response_to_key_server_request = None
        self.__class__.mac_algorithm_response_to_key_server_request = None
        self.__class__.owner_in_response_to_key_server_request = None
        self.__class__.asrs.reset()

    def assertMACKeyIdentifierInKeyServerRequest(self, mac_key_identifier):
        """The unit test that was just run caused the authentication server
        to call out (perhaps) to the key server. The authentication server
        made this call with a particular MAC key identifier. This method
        allows to caller to assert which MAC key identifier was sent to the
        key server."""
        if mac_key_identifier is None:
            self.assertIsNone(
                self.__class__._mac_key_identifier_in_key_server_request)
        else:
            self.assertEqual(
                self.__class__._mac_key_identifier_in_key_server_request,
                mac_key_identifier)

    def assertAuthHdrInReqToAppServer(
        self,
        expected_auth_method,
        expected_owner,
        expected_id):
        """The unit test that was just run caused the authentication server
        to forward a request to the app server. The authentication server
        made this call with a particular authorization header. This method
        allows to caller to assert that the format and content of the
        authorization header was as expected."""
        self.assertIsNotNone(self.__class__.asrs.auth_hdr_in_req)
        reg_ex_pattern = (
            '^\s*'
            '(?P<auth_method>[^\s]+)\s+'
            '(?P<owner>[^\s]+)\s+'
            '(?P<id>[^\s]+)\s*'
            '$'
        )
        reg_ex = re.compile(reg_ex_pattern, re.IGNORECASE)
        match = reg_ex.match(self.__class__.asrs.auth_hdr_in_req)
        self.assertIsNotNone(match)
        assert 0 == match.start()
        assert len(self.__class__.asrs.auth_hdr_in_req) == match.end()
        assert 3 == len(match.groups())
        auth_method = match.group("auth_method")
        assert auth_method is not None
        assert 0 < len(auth_method)
        owner = match.group("owner")
        assert owner is not None
        assert 0 < len(owner)
        id = match.group("id")
        assert id is not None
        assert 0 < len(id)
        self.assertEqual(auth_method, expected_auth_method)
        self.assertEqual(owner, expected_owner)
        self.assertEqual(id, expected_id)

    def assertAppServerRequest(
        self,
        get=False,
        post=False,
        delete=False,
        put=False):
        """The unit test that was just run caused the authentication server
        to forward a request to the app server. This method allows the caller
        to assert that the app server recieved the correct request."""
        self.assertEqual(self.__class__.asrs.received_get, get)
        self.assertEqual(self.__class__.asrs.received_post, post)
        self.assertEqual(self.__class__.asrs.received_put, put)
        self.assertEqual(self.__class__.asrs.received_delete, delete)

    def assertAuthFailure(self, response, detail):
        self.assertEqual(response.status, httplib.UNAUTHORIZED)
        header_name = "x-auth-server-auth-failure-detail"
        self.assertIn(header_name, response)
        value = response.get(header_name, None)
        self.assertEqual(value, detail)

    def test_get_with_no_authorization_header(self):
        http_client = httplib2.Http()
        response, content = http_client.request(
            "http://localhost:%d/whatever" % self.__class__.auth_server.port,
            "GET")
        self.assertAuthFailure(
            response,
            auth_server.AUTH_FAILURE_DETAIL_NO_AUTH_HEADER)

    def test_get_with_invalid_authorization_header(self):
        http_client = httplib2.Http()
        response, content = http_client.request(
            "http://localhost:%d/whatever" % self.__class__.auth_server.port,
            "GET",
            headers={
                "Authorization":
                'MAC id="", ts="890", nonce="98", ext="abc", mac="bindle"'
            })
        self.assertAuthFailure(
            response,
            auth_server.AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER)

    def test_invalid_mac_algorithm_returned_from_key_server(self):
        mac_key_identifier = mac.MACKeyIdentifier.generate()
        mac_key = mac.MACKey.generate()
        mac_algorithm = mac.MAC.algorithm
        owner = str(uuid.uuid4())
        http_method = "GET"
        uri = "/whatever"
        host = "localhost"
        port = self.__class__.auth_server.port
        content_type = None
        body = None

        self.__class__.mac_key_in_response_to_key_server_request = mac_key
        self.__class__.mac_algorithm_response_to_key_server_request = \
            "dave-%s" % mac_algorithm
        self.__class__.owner_in_response_to_key_server_request = owner

        ts = mac.Timestamp.generate()
        nonce = mac.Nonce.generate()
        ext = mac.Ext.generate(content_type, body)
        normalized_request_string = mac.NormalizedRequestString.generate(
            ts,
            nonce,
            http_method,
            uri,
            host,
            port,
            ext)
        my_mac = mac.MAC.generate(
            mac_key,
            mac_algorithm,
            normalized_request_string)
        auth_header_value = mac.AuthHeaderValue(
            mac_key_identifier,
            ts,
            nonce,
            ext,
            my_mac)
        auth_header_value = str(auth_header_value)
        http_client = httplib2.Http()
        response, content = http_client.request(
            "http://%s:%d%s" % (host, port, uri),
            http_method,
            headers={"Authorization": auth_header_value})
        self.assertTrue(response.status == httplib.OK)
        self.assertAppServerRequest(get=True)
        self.assertMACKeyIdentifierInKeyServerRequest(mac_key_identifier)
        self.assertAuthHdrInReqToAppServer(
            self.__class__.app_server_auth_method,
            owner,
            mac_key_identifier)

    def test_all_good_on_post(self):
        mac_key_identifier = mac.MACKeyIdentifier.generate()
        mac_key = mac.MACKey.generate()
        mac_algorithm = mac.MAC.algorithm
        owner = str(uuid.uuid4())
        http_method = "POST"
        uri = "/isallokonpost"
        host = "localhost"
        port = self.__class__.auth_server.port
        content_type = "application/json; charset=utf-8"
        body = json.dumps({"dave": "was", "here": "today"})

        self.__class__.mac_key_in_response_to_key_server_request = mac_key
        self.__class__.mac_algorithm_response_to_key_server_request = \
            mac_algorithm
        self.__class__.owner_in_response_to_key_server_request = owner

        ts = mac.Timestamp.generate()
        nonce = mac.Nonce.generate()
        ext = mac.Ext.generate(content_type, body)
        normalized_request_string = mac.NormalizedRequestString.generate(
            ts,
            nonce,
            http_method,
            uri,
            host,
            port,
            ext)
        my_mac = mac.MAC.generate(
            mac_key,
            mac_algorithm,
            normalized_request_string)
        auth_header_value = mac.AuthHeaderValue(
            mac_key_identifier,
            ts,
            nonce,
            ext,
            my_mac)
        auth_header_value = str(auth_header_value)
        http_client = httplib2.Http()
        headers = {
            "Authorization": str(auth_header_value),
            "Content-Type": content_type,
        }
        response, content = http_client.request(
            "http://%s:%d%s" % (host, port, uri),
            http_method,
            headers=headers,
            body=body)
        self.assertTrue(response.status == httplib.OK)
        self.assertAppServerRequest(post=True)
        self.assertMACKeyIdentifierInKeyServerRequest(mac_key_identifier)
        self.assertAuthHdrInReqToAppServer(
            self.__class__.app_server_auth_method,
            owner,
            mac_key_identifier)

    def _send_get_to_auth_server(
        self,
        mac_key_identifier,
        mac_key,
        mac_algorithm,
        owner,
        seconds_to_subtract_from_ts=None):
        """Utility method for issuing HTTP GETs to the auth server
        with the provided credentials."""

        http_method = "GET"
        uri = "/whatever"
        host = "localhost"
        port = self.__class__.auth_server.port
        content_type = None
        body = None

        ts = mac.Timestamp.generate()
        if seconds_to_subtract_from_ts is not None:
            ts = mac.Timestamp(int(ts) - seconds_to_subtract_from_ts)
        nonce = mac.Nonce.generate()
        ext = mac.Ext.generate(content_type, body)
        normalized_request_string = mac.NormalizedRequestString.generate(
            ts,
            nonce,
            http_method,
            uri,
            host,
            port,
            ext)
        my_mac = mac.MAC.generate(
            mac_key,
            mac_algorithm,
            normalized_request_string)
        auth_header_value = mac.AuthHeaderValue(
            mac_key_identifier,
            ts,
            nonce,
            ext,
            my_mac)

        http_client = httplib2.Http()
        response, content = http_client.request(
            "http://localhost:%d%s" % (self.__class__.auth_server.port, uri),
            "GET",
            headers={"Authorization": str(auth_header_value)})

        self.assertAppServerRequest(get=True)
        self.assertMACKeyIdentifierInKeyServerRequest(mac_key_identifier)
        self.assertAuthHdrInReqToAppServer(
            self.__class__.app_server_auth_method,
            owner,
            mac_key_identifier)
        if response.status == httplib.OK:
            self.assertAuthHdrInReqToAppServer(
                self.__class__.app_server_auth_method,
                owner,
                mac_key_identifier)

        return (response, content)

    def test_get_with_old_timestamp(self):
        # establish credentials
        mac_key_identifier = mac.MACKeyIdentifier.generate()
        mac_key = mac.MACKey.generate()
        mac_algorithm = mac.MAC.algorithm
        owner = str(uuid.uuid4())

        # configure mock key server with established credentials
        self.__class__.mac_key_in_response_to_key_server_request = mac_key
        self.__class__.mac_algorithm_response_to_key_server_request = \
            mac_algorithm
        self.__class__.owner_in_response_to_key_server_request = owner

        # initially confirm all good with a simple GET request
        response, content = self._send_get_to_auth_server(
            mac_key_identifier,
            mac_key,
            mac_algorithm,
            owner)
        self.assertTrue(response.status == httplib.OK)

        # now repeat the all good GET but this time ask for the request's
        # timestamp to be reduced by # of seconds in one year
        one_year_in_seconds = 365*24*60
        response, content = self._send_get_to_auth_server(
            mac_key_identifier,
            mac_key,
            mac_algorithm,
            owner,
            seconds_to_subtract_from_ts=one_year_in_seconds)
        self.assertAuthFailure(
            response,
            auth_server.AUTH_FAILURE_DETAIL_TS_OLD)

        # now repeat the all good GET but this time ask for the request's
        # timestamp to be advanced by one day
        one_day_in_seconds = 24*60
        response, content = self._send_get_to_auth_server(
            mac_key_identifier,
            mac_key,
            mac_algorithm,
            owner,
            seconds_to_subtract_from_ts=-one_day_in_seconds)
        self.assertAuthFailure(
            response,
            auth_server.AUTH_FAILURE_DETAIL_TS_IN_FUTURE)

    def test_get_with_unknonwn_mac_key_identifier(self):
        # establish credentials
        mac_key_identifier = mac.MACKeyIdentifier.generate()
        mac_key = mac.MACKey.generate()
        mac_algorithm = mac.MAC.algorithm
        owner = str(uuid.uuid4())

        # configure mock key server with established credentials
        self.__class__.mac_key_in_response_to_key_server_request = mac_key
        self.__class__.mac_algorithm_response_to_key_server_request = \
            mac_algorithm
        self.__class__.owner_in_response_to_key_server_request = owner

        # initially confirm all good with a simple GET request
        response, content = self._send_get_to_auth_server(
            mac_key_identifier,
            mac_key,
            mac_algorithm,
            owner)
        self.assertTrue(response.status == httplib.OK)

        # now repeat the all good GET but this time tell the mock key server
        # to claim it doesn't have creds for the mac key identifier
        self.__class__.status_code_of_response_to_key_server_request = \
            httplib.NOT_FOUND

        response, content = self._send_get_to_auth_server(
            mac_key_identifier,
            mac_key,
            mac_algorithm,
            owner)
        self.assertAuthFailure(
            response,
            auth_server.AUTH_FAILURE_DETAIL_CREDS_NOT_FOUND)
