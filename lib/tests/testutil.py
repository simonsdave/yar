"""This module contains a collection of generally useful utilities
when writing unit tests for various components of the API management
solution."""


import httplib
import json
import logging
import socket
import re
import subprocess
import sys
import threading
import unittest

import memcache
import tornado.netutil
import tornado.ioloop

_logger = logging.getLogger("UTIL.%s" % __name__)

__version__ = "1.0"


class TestCase(unittest.TestCase):

    def assertIsJsonUtf8ContentType(self, content_type):
        """Allows the caller to assert if ```content_type```
        is valid for specifying utf8 json content in an http header. """
        self.assertIsNotNone(content_type)
        json_utf8_content_type_reg_ex = re.compile(
            "^\s*application/json;\s+charset\=utf-{0,1}8\s*$",
            re.IGNORECASE)
        self.assertIsNotNone(json_utf8_content_type_reg_ex.match(content_type))


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


class Server(object):
    """An abstract base class for mock auth server, key server and
    app server. The primary reason for this class to exist is so the
    constructor can find an available port for the server to run and
    save that port & associated socket object in the socket and
    port properties."""

    def __init__(self, is_in_process=True):
        """Opens a random but available socket and assigns it to the
        socket property. The socket's port is also assigned to the
        port property."""
        object.__init__(self)

        if is_in_process:
            [self.socket] = tornado.netutil.bind_sockets(
                0,
                "localhost",
                family=socket.AF_INET)
            self.port = self.socket.getsockname()[1]
        else:
            # :TODO: there has to be a better way to do this.
            # Original motivation for this was the desire to
            # start a memcached process on an available port.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('', 0))
            self.port = self.socket.getsockname()[1]
            self.socket.close()
            self.socket = None

    def shutdown(self):
        """Can be overriden by derived classes to perform server
        type specific shutdown. This method is a no-op but derived
        classes should call this method in case this is not a no-op
        in the future."""
        pass


class NonceStore(Server):
    """The mock nonce store."""

    def __init__(self):
        """Starts memcached on a random but available port.
        Yes this class really does spawn a memcached process.
        :TODO: Is there a way to start an in-memory or mock
        version of memcached?"""
        Server.__init__(self, is_in_process=False)

        args = [
            "memcached",
            # "-vv",
            "-p",
            str(self.port),
            "-U",
            str(self.port),
            "-l",
            "localhost"
        ]
        self._process = subprocess.Popen(args, shell=False)

        key = "some_key"
        value = None
        number_attempts = 10
        for attempt in range(0, number_attempts):
            mc = memcache.Client(self.memcached_cluster, debug=1)
            mc.set(key, "some value")
            if mc.get(key):
                break

    def shutdown(self):
        """Terminate the memcached process implementing the
        nonce store."""
        if self._process:
            self._process.terminate()
            self._process = None

        Server.shutdown(self)

    @property
    def memcached_cluster(self):
        """memcached clients reference a memcached cluster
        with knowledge of entire cluster's ip+port pairs.
        While ```NonceStore``` implements a cluster
        of a single memcached instance, the array of ip+port
        pairs still needs to be passed to memcached clients.
        This is a convience method for constructing the
        array of which describes to memcached clients how
        a memcached client can access the nonce store
        cluster."""
        return ["localhost:%d" % self.port]


class AppServerRequestState(object):

    def __init__(self):
        object.__init__(self)

    def reset(self):
        self.auth_hdr_in_req = None
        self.received_get = False
        self.received_post = False
        self.received_put = False
        self.received_delete = False


class AppServerRequestHandler(tornado.web.RequestHandler):
    """Tornado request handler for use by the mock app server. This request
    handler only implements HTTP GET."""

    asrs = None

    def _handle_request(self, get=False, post=False, put=False, delete=False):
        asrs = self.__class__.asrs
        asrs.auth_hdr_in_req = self.request.headers.get(
            "Authorization",
            None)
        asrs.received_post = post
        asrs.received_get = get
        asrs.received_put = put
        asrs.received_delete = delete
        self.set_status(httplib.OK)

    def get(self):
        self._handle_request(get=True)

    def post(self):
        self._handle_request(post=True)

    def put(self):
        self._handle_request(put=True)

    def delete(self):
        self._handle_request(delete=True)


class AppServer(Server):
    """The mock app server."""

    def __init__(self, asrs):
        """Creates an instance of the mock app server and starts the
        server listenting on a random, available port."""
        Server.__init__(self)

        handler_cls = AppServerRequestHandler
        handler_cls.asrs = asrs
        handlers = [(r".*", handler_cls)]
        app = tornado.web.Application(handlers=handlers)
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.add_sockets([self.socket])


class KeyServerRequestState(object):

    def __init__(self):
        object.__init__(self)

        self.reset()

    def reset(self):
        self.mac_key_identifier_in_request = None
        self.status_code_of_response = None
        self.content_type_of_response = None
        self.body_of_response = None
        self.mac_key_in_response = None
        self.mac_algorithm_in_response = None
        self.owner_in_response = None


class KeyServerRequestHandler(tornado.web.RequestHandler):
    """Tornado request handler for use by the mock key server. This request
    handler only implements HTTP GET since that's the only type of request the
    auth server issues to the key server."""

    ksrs = None

    def get(self):
        """Implements HTTP GET for the mock key server."""

        ksrs = self.__class__.ksrs

        uri_reg_ex = re.compile(
            '^/v1\.0/creds/(?P<mac_key_identifier>.+)$',
            re.IGNORECASE)
        match = uri_reg_ex.match(self.request.uri)
        if not match:
            ksrs.mac_key_identifier_in_request = None
            self.set_status(httplib.BAD_REQUEST)
        else:
            assert 0 == match.start()
            assert len(self.request.uri) == match.end()
            assert 1 == len(match.groups())
            mac_key_identifier = match.group("mac_key_identifier")
            assert mac_key_identifier is not None
            assert 0 < len(mac_key_identifier)

            ksrs.mac_key_identifier_in_request = mac_key_identifier

            status = \
                ksrs.status_code_of_response \
                or \
                httplib.OK
            self.set_status(status)

            if status == httplib.OK:
                dict = ksrs.body_of_response \
                    or \
                    {
                        "is_deleted": False,
                        "mac_algorithm": ksrs.mac_algorithm_in_response,
                        "mac_key": ksrs.mac_key_in_response,
                        "mac_key_identifier": mac_key_identifier,
                        "owner": ksrs.owner_in_response or str(uuid.uuid4()),
                    }
                body = json.dumps(dict)
                self.write(body)

                self.set_header(
                    ksrs.content_type_of_response
                    or
                    "Content-Type", "application/json; charset=utf8")


class KeyServer(Server):
    """The mock key server."""

    def __init__(self, ksrs):
        """Creates an instance of the mock key server and starts the
        server listenting on a random, available port."""
        Server.__init__(self)

        handler_cls = KeyServerRequestHandler
        handler_cls.ksrs = ksrs
        handlers = [(r".*", handler_cls)]
        app = tornado.web.Application(handlers=handlers)
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.add_sockets([self.socket])
