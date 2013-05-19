"""This module contains the auth server's unit tests."""

import logging
import unittest
import httplib
import httplib2
import json
import uuid
import threading
import re

import tornado.httpserver
import tornado.ioloop
import tornado.web

import auth_server
import testutil
import mac

_logger = logging.getLogger(__name__)


class Server(object):
    """An abstract base class for mock auth server, key server and
    app server. The primary reason for this class to exist is so the
    constructor can find an available port for the server to run and
    save that port & associated socket object in the socket and
    port properties."""

    def __init__(self):
        """Opens a random but available socket and assigns it to the
        socket property. The socket's port is also assigned to the
        port property."""
        object.__init__(self)

        (self.socket, self.port) = testutil.get_available_port()


class AppServerRequestHandler(tornado.web.RequestHandler):
    """Tornado request handler for use by the mock app server. This request
    handler only implements HTTP GET."""

    def _save_authorization_header_value(self):
        TestCase.auth_hdr_in_req_to_app_server = \
            self.request.headers.get("Authorization", None)

    def get(self):
        """Implements HTTP GET for the mock app server."""
        TestCase.app_server_received_get = True
        self._save_authorization_header_value()
        self.set_status(httplib.OK)

    def post(self):
        """Implements HTTP POST for the mock app server."""
        TestCase.app_server_received_post = True
        self._save_authorization_header_value()
        self.set_status(httplib.OK)

    def put(self):
        """Implements HTTP PUT for the mock app server."""
        TestCase.app_server_received_put = True
        self._save_authorization_header_value()
        self.set_status(httplib.OK)

    def delete(self):
        """Implements HTTP DELETE for the mock app server."""
        TestCase.app_server_received_delete = True
        self._save_authorization_header_value()
        self.set_status(httplib.OK)


class AppServer(Server):
    """The mock app server."""

    def __init__(self):
        """Creates an instance of the mock app server and starts the
        server listenting on a random, available port."""
        Server.__init__(self)

        handlers = [(r".*", AppServerRequestHandler)]
        app = tornado.web.Application(handlers=handlers)
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.add_sockets([self.socket])


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


class KeyServer(Server):
    """The mock key server."""

    def __init__(self):
        """Creates an instance of the mock key server and starts the
        server listenting on a random, available port."""
        Server.__init__(self)

        handlers = [(r".*", KeyServerRequestHandler)]
        app = tornado.web.Application(handlers=handlers)
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.add_sockets([self.socket])


class AuthenticationServer(Server):
    """Mock authentication server."""

    def __init__(self, key_server, app_server, app_server_auth_method):
        """Creates an instance of the auth server and starts the
        server listenting on a random, available port."""
        Server.__init__(self)

        auth_server.key_server = "localhost:%d" % key_server.port
        auth_server.app_server = "localhost:%d" % app_server.port
        auth_server.app_server_auth_method = app_server_auth_method
        auth_server.include_auth_failure_detail = True
        # :TODO: ...
        auth_server.nonce_store = ["localhost:11211"]
        # :TODO: ...

        http_server = tornado.httpserver.HTTPServer(auth_server._tornado_app)
        http_server.add_sockets([self.socket])


class IOLoop(threading.Thread):
    """This class makes it easy for a test case's `setUpClass()` to start
    a Tornado io loop on the non-main thread so that the io loop, auth server
    key server and app server can operate 'in the background' while the
    unit test runs on the main thread."""

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        tornado.ioloop.IOLoop.instance().stop()


class TestCase(testutil.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app_server = AppServer()
        cls.app_server_auth_method = str(uuid.uuid4()).replace("-", "")
        cls.key_server = KeyServer()
        cls.auth_server = AuthenticationServer(
            cls.key_server,
            cls.app_server,
            cls.app_server_auth_method)

        cls.io_loop = IOLoop()
        cls.io_loop.start()

    @classmethod
    def tearDownClass(cls):
        cls.app_server = None
        cls.auth_server = None
        cls.key_server = None
        cls.io_loop.stop()
        cls.io_loop = None

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

    """When the auth server forwards a request to the app server the
    request's authorization header contained the value found
    in '''auth_hdr_in_req_to_app_server```."""
    auth_hdr_in_req_to_app_server = None

    """When the app server recieves a GET it sets
    ```app_server_received_post``` to True."""
    app_server_received_get = None

    """When the app server recieves a POST it sets
    ```app_server_received_post``` to True."""
    app_server_received_post = None

    """When the app server recieves a PUT it sets
    ```app_server_received_post``` to True."""
    app_server_received_put = None

    """When the app server recieves a DELETE it sets
    ```app_server_received_delete``` to True."""
    app_server_received_delete = None

    """When the app server recieves a HEAD it sets
    ```app_server_received_head``` to True."""
    app_server_received_head = None

    """When the app server recieves a OPTIONS it sets
    ```app_server_received_options``` to True."""
    app_server_received_options = None

    def setUp(self):
        testutil.TestCase.setUp(self)
        self.__class__._mac_key_identifier_in_key_server_request = None
        self.__class__.status_code_of_response_to_key_server_request = None
        self.__class__.content_type_of_response_to_key_server_request = None
        self.__class__.body_of_response_to_key_server_request = None
        self.__class__.mac_key_in_response_to_key_server_request = None
        self.__class__.mac_algorithm_response_to_key_server_request = None
        self.__class__.owner_in_response_to_key_server_request = None
        self.__class__.auth_hdr_in_req_to_app_server = None
        self.__class__.app_server_received_get = False
        self.__class__.app_server_received_post = False
        self.__class__.app_server_received_put = False
        self.__class__.app_server_received_delete = False
        self.__class__.app_server_received_head = False
        self.__class__.app_server_received_options = False

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
        self.assertIsNotNone(self.__class__.auth_hdr_in_req_to_app_server)
        reg_ex_pattern = (
            '^\s*'
            '(?P<auth_method>[^\s]+)\s+'
            '(?P<owner>[^\s]+)\s+'
            '(?P<id>[^\s]+)\s*'
            '$'
        )
        reg_ex = re.compile(reg_ex_pattern, re.IGNORECASE)
        match = reg_ex.match(self.__class__.auth_hdr_in_req_to_app_server)
        self.assertIsNotNone(match)
        assert 0 == match.start()
        assert len(self.__class__.auth_hdr_in_req_to_app_server) == match.end()
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
        put=False,
        head=False,
        options=False):
        """The unit test that was just run caused the authentication server
        to forward a request to the app server. This method allows the caller
        to assert that the app server recieved the correct request."""
        self.assertEqual(self.__class__.app_server_received_get, get)
        self.assertEqual(self.__class__.app_server_received_post, post)
        self.assertEqual(self.__class__.app_server_received_put, put)
        self.assertEqual(self.__class__.app_server_received_delete, delete)
        self.assertEqual(self.__class__.app_server_received_head, head)
        self.assertEqual(self.__class__.app_server_received_options, options)

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
