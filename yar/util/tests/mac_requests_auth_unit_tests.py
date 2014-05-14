"""This module contains a series of unit tests which
validate yar.util.mac.RequestsAuth's functionality."""

import BaseHTTPServer
import threading
import time
import unittest

import mock
import requests

from yar.util import mac
from yar.tests import yar_test_util


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def log_message( format, *arg ):
        """yes this really is meant to be a no-op"""
        pass

    def do_PUT( self ):
        # content_length = int(self.headers.getheader("content-length")
        # content = StringIO.StringIO(self.rfile.read(content_length))
        pass


class HTTPServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        self.ip = "127.0.0.1"
        httpd = BaseHTTPServer.HTTPServer(
            (self.ip, 0),
            RequestHandler)
        self.port = httpd.server_port
        httpd.serve_forever()
        "never returns"

    def start(self):
        threading.Thread.start( self )
        # give the HTTP server time to start & initialize itself
        while 'port' not in self.__dict__:
            time.sleep(1)

class TestRequestsAuth(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._http_server = HTTPServer()
        cls._http_server.start()

    @classmethod
    def tearDownClass(cls):
        cls._http_server = None

    def _dave_(self):
        cls = type(self)

        url = "http://%s:%s/dave.html" % (
            cls._http_server.ip,
            cls._http_server.port
        )

        mac_key_identifier = mac.MACKeyIdentifier.generate()
        mac_key = mac.MACKey.generate()
        mac_algorithm = mac.MAC.algorithm

        auth = mac.RequestsAuth(
            mac_key_identifier,
            mac_key,
            mac_algorithm)

        response = requests.get(url, auth=auth)
        print response.status_code

    def test_all_good_get(self):

        mac_key_identifier = mac.MACKeyIdentifier.generate()
        mac_key = mac.MACKey.generate()
        mac_algorithm = mac.MAC.algorithm

        auth = mac.RequestsAuth(
            mac_key_identifier,
            mac_key,
            mac_algorithm)

        mock_request = mock.Mock()
        mock_request.headers = {}
        mock_request.body = None
        mock_request.method = "GET"
        mock_request.url = "http://localhost:8000"

        rv = auth(mock_request)

        self.assertIsNotNone(rv)
        self.assertIs(rv, mock_request)
        self.assertTrue("Authorization" in mock_request.headers)
        ahv = mac.AuthHeaderValue.parse(mock_request.headers["Authorization"])
        self.assertIsNotNone(ahv)
        self.assertEqual(ahv.mac_key_identifier, mac_key_identifier)
        self.assertEqual(ahv.ext, "")
