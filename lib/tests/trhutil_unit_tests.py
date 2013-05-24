"""This module contains a collection of unit tests
for the ```trhutil``` module."""

import httplib
import json
import os
import sys
import unittest
import uuid

import tornado.web
import tornado.testing

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import trhutil

def _uuid():
    return str(uuid.uuid4()).replace("-", "")

class GetRequestHostAndPortRequestHandler(trhutil.RequestHandler):

    host_if_not_found = _uuid()
    port_if_not_found = -1

    def get(self):
        delete_host = self.get_argument("delete_host", False)
        if delete_host:
            del self.request.headers["Host"]
        (host, port) = self.get_request_host_and_port(
            self.__class__.host_if_not_found,
            self.__class__.port_if_not_found)
        response_body = {
            "host": host,
            "port": port
        }
        self.write(response_body)
        self.set_status(httplib.OK)

class GetRequestHostAndPortTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        handlers = [(r".*", GetRequestHostAndPortRequestHandler), ]
        app = tornado.web.Application(handlers=handlers)
        return app

    def _do_it(self, host_header_value, expected_host, expected_port):
        query_string = ""
        headers = {}
        if host_header_value is None:
            query_string = "?delete_host=1"
        else:
            headers = {"host": host_header_value}
        self.http_client.fetch(
            self.get_url(query_string), 
            self.stop,
            headers=tornado.httputil.HTTPHeaders(headers))
        response = self.wait()
        self.assertIsNotNone(response)
        self.assertEqual(response.code, httplib.OK)
        response_as_dict = json.loads(response.body)
        self.assertTrue("host" in response_as_dict)
        self.assertEquals(response_as_dict["host"], expected_host)
        self.assertTrue("port" in response_as_dict)
        self.assertEquals(response_as_dict["port"], expected_port)

    def test_all_good(self):
        self._do_it("dave:42", "dave", "42")

    def test_good_with_port_missing(self):
        self._do_it("dave", "dave", RequestHandler.port_if_not_found)

    def test_zero_length_string_host(self):
        self._do_it(
            "",
            RequestHandler.host_if_not_found,
            RequestHandler.port_if_not_found)

    def test_port_with_no_host(self):
        self._do_it(
            ":42",
            RequestHandler.host_if_not_found,
            RequestHandler.port_if_not_found)

    def test_no_host_http_hearder(self):
        self._do_it(
            None,
            RequestHandler.host_if_not_found,
            RequestHandler.port_if_not_found)

class GetRequestIfExistsRequestHandler(trhutil.RequestHandler):

    body_if_not_found = _uuid()
    port_if_not_found = -1

    def get(self):
        delete_host = self.get_argument("delete_host", False)
        if delete_host:
            del self.request.headers["Host"]
        (host, port) = self.get_request_host_and_port(
            self.__class__.host_if_not_found,
            self.__class__.port_if_not_found)
        response_body = {
            "host": host,
            "port": port
        }
        self.write(response_body)
        self.set_status(httplib.OK)

class GetRequestHostAndPortTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        handlers = [(r".*", GetRequestHostAndPortRequestHandler), ]
        app = tornado.web.Application(handlers=handlers)
        return app

    def _do_it(self, host_header_value, expected_host, expected_port):
        query_string = ""
        headers = {}
        if host_header_value is None:
            query_string = "?delete_host=1"
        else:
            headers = {"host": host_header_value}
        self.http_client.fetch(
            self.get_url(query_string), 
            self.stop,
            headers=tornado.httputil.HTTPHeaders(headers))
        response = self.wait()
        self.assertIsNotNone(response)
        self.assertEqual(response.code, httplib.OK)
        response_as_dict = json.loads(response.body)
        self.assertTrue("host" in response_as_dict)
        self.assertEquals(response_as_dict["host"], expected_host)
        self.assertTrue("port" in response_as_dict)
        self.assertEquals(response_as_dict["port"], expected_port)

    def test_all_good(self):
        self._do_it("dave:42", "dave", "42")

    def test_good_with_port_missing(self):
        self._do_it(
            "dave",
            "dave",
            GetRequestHostAndPortRequestHandler.port_if_not_found)

    def test_zero_length_string_host(self):
        self._do_it(
            "",
            GetRequestHostAndPortRequestHandler.host_if_not_found,
            GetRequestHostAndPortRequestHandler.port_if_not_found)

    def test_port_with_no_host(self):
        self._do_it(
            ":42",
            GetRequestHostAndPortRequestHandler.host_if_not_found,
            GetRequestHostAndPortRequestHandler.port_if_not_found)

    def test_no_host_http_hearder(self):
        self._do_it(
            None,
            GetRequestHostAndPortRequestHandler.host_if_not_found,
            GetRequestHostAndPortRequestHandler.port_if_not_found)

class GetRequestBodyIfExistsRequestHandler(trhutil.RequestHandler):

    body_if_not_found = _uuid()
    def post(self):
        response_body = self.get_request_body_if_exists(
            self.__class__.body_if_not_found)
        self.write(response_body)
        self.set_status(httplib.OK)

class GetRequestBodyIfExistsTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        handlers = [(r".*", GetRequestBodyIfExistsRequestHandler), ]
        app = tornado.web.Application(handlers=handlers)
        return app

    def _do_it(self, body, expected_body):
        # headers = {"Content-length": len(body)}
        headers = {}
        self.http_client.fetch(
            self.get_url(""), 
            self.stop,
            method="POST",
            headers=tornado.httputil.HTTPHeaders(headers),
            body=body)
        response = self.wait()
        self.assertIsNotNone(response)
        self.assertEqual(response.code, httplib.OK)
        self.assertEqual(response.body, expected_body)

    def test_all_good_non_zero_length_body(self):
        body = _uuid()
        self._do_it(body, body)

    def test_all_good_zero_length_body(self):
        body = ""
        self._do_it(body, body)
