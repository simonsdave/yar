"""This module contains a collection of generally useful utilities
when writing unit tests for various components of the API management
solution."""


import logging
import socket
import re
import unittest

import tornado.netutil


_logger = logging.getLogger("UTIL.%s" % __name__)


__version__ = "1.0"


def get_available_port():
    """Return an available socket and the associated port."""
    [avail_socket] = tornado.netutil.bind_sockets(
        0,
        "localhost",
        family=socket.AF_INET)
    avail_port = avail_socket.getsockname()[1]
    return (avail_socket, avail_port)


class TestCase(unittest.TestCase):

    def assertIsJsonUtf8ContentType(self, content_type):
        """Allows the caller to assert if ```content_type```
        is valid for specifying utf8 json content in an http header. """
        self.assertIsNotNone(content_type)
        json_utf8_content_type_reg_ex = re.compile(
            "^\s*application/json;\s+charset\=utf-{0,1}8\s*$",
            re.IGNORECASE)
        self.assertIsNotNone(json_utf8_content_type_reg_ex.match(content_type))
