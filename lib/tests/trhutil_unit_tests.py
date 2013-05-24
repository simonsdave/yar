"""This module contains a collection of unit tests
for the ```trhutil``` module."""

import json
import httplib
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tornado.web
import tornado.testing

import trhutil

class RequestHandler(trhutil.RequestHandler):

    def get(self):
        (host, port) = self.get_request_host_and_port()
        body = {
            "host": host,
            "port": port
        }
        self.write(body)
        self.set_status(httplib.OK)

class AsyncAppTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        handlers = [(r".*", RequestHandler), ]
        app = tornado.web.Application(handlers=handlers)
        return app

    def get_http_port(self):
        self._port = tornado.testing.AsyncHTTPTestCase.get_http_port(self)
        return self._port

    def test_get_request_host_and_port(self):
        self.http_client.fetch(self.get_url('/'), self.stop)
        response = self.wait()
        response_as_dict = json.loads(response.body)
        self.assertTrue("host" in response_as_dict)
        self.assertEquals(response_as_dict["host"], "localhost")
        self.assertTrue("port" in response_as_dict)
        self.assertEquals(response_as_dict["port"], self._port)
