"""This module contains a collection of generally useful utilities
when writing unit tests for various components of the API management
solution."""


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
