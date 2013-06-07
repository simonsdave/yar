"""This module contains a collection of utilities for
the auth server's unit tests."""

import logging
import os
import socket
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tornado.ioloop

_logger = logging.getLogger(__name__)


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

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('', 0))
        self.port = self.socket.getsockname()[1]

        if not is_in_process:
            self.socket.close()
            self.socket = None

    def shutdown(self):
        """Can be overriden by derived classes to perform server
        type specific shutdown. This method is a no-op but derived
        classes should call this method in case this is not a no-op
        in the future."""
        pass
