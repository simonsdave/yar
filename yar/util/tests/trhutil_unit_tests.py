"""This module contains a collection of unit tests
for the ```trhutil``` module."""

import httplib
import json
import os
import sys
import unittest
import uuid

import mock
import tornado.web
import tornado.testing

from yar.util import trhutil

def _uuid():
    return str(uuid.uuid4()).replace("-", "")


class IsJSONContentTypeTestCase(unittest.TestCase):

    def test_none_content_type(self):
        self.assertFalse(trhutil._is_json_content_type(None))

    def test_valid_content_type_001(self):
        self.assertTrue(trhutil._is_json_content_type("application/json"))

    def test_valid_content_type_002(self):
        self.assertTrue(trhutil._is_json_content_type("  application/json"))

    def test_valid_content_type_003(self):
        self.assertTrue(trhutil._is_json_content_type("application/json   "))

    def test_valid_content_type_004(self):
        self.assertTrue(trhutil._is_json_content_type("application/JSON"))

    def test_invalid_content_type(self):
        self.assertFalse(trhutil._is_json_content_type("dave"))


class IsJSONUTF8ContentTypeTestCase(unittest.TestCase):

    def test_none_content_type(self):
        self.assertFalse(trhutil._is_json_utf8_content_type(None))

    def test_valid_content_type_001(self):
        self.assertFalse(trhutil._is_json_utf8_content_type("application/json;charset=utf-8"))

    def test_valid_content_type_002(self):
        self.assertTrue(trhutil._is_json_utf8_content_type("APPLICATION/json; charset=utf-8"))

    def test_valid_content_type_003(self):
        self.assertTrue(trhutil._is_json_utf8_content_type("application/json;  charset=utf-8"))

    def test_valid_content_type_004(self):
        self.assertTrue(trhutil._is_json_utf8_content_type("  application/json; charset=utf-8"))

    def test_valid_content_type_005(self):
        self.assertTrue(trhutil._is_json_utf8_content_type("application/json; charset=utf-8   "))

    def test_valid_content_type_006(self):
        self.assertTrue(trhutil._is_json_utf8_content_type("application/json; charset=utf8"))

    def test_invalid_content_type(self):
        self.assertFalse(trhutil._is_json_utf8_content_type("dave"))


class GetRequestBodyIfExistsTestCase(unittest.TestCase):

    def test_no_content_length_or_transfer_encoding_headers_001(self):
        request = mock.Mock()
        request.headers = {}
        self.assertIsNone(trhutil.get_request_body_if_exists(request))

    def test_no_content_length_or_transfer_encoding_headers_002(self):
        request = mock.Mock()
        request.headers = {}
        value_if_not_found = "bindle"
        self.assertEqual(
            trhutil.get_request_body_if_exists(request, value_if_not_found),
            value_if_not_found)

    def test_content_length_in_headers_but_no_body_001(self):
        request = mock.Mock()
        request.headers = {"Content-Length": 10}
        request.body = None
        self.assertIsNone(trhutil.get_request_body_if_exists(request))

    def test_content_length_in_headers_but_no_body_002(self):
        request = mock.Mock()
        request.headers = {"Content-Length": 10}
        request.body = None
        value_if_not_found = "bindle"
        self.assertEqual(
            trhutil.get_request_body_if_exists(request, value_if_not_found),
            value_if_not_found)

    def test_all_good_001(self):
        request = mock.Mock()
        request.headers = {"Content-Length": 10}
        request.body = "dave was here"
        self.assertEqual(
            trhutil.get_request_body_if_exists(request),
            request.body)

    def test_all_good_002(self):
        request = mock.Mock()
        request.headers = {"Transfer-Encoding": 10}
        request.body = "dave was here"
        self.assertEqual(
            trhutil.get_request_body_if_exists(request),
            request.body)


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


class GetRequestHostAndPortRequestHandlerTestCase(tornado.testing.AsyncHTTPTestCase):

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


class GetRequestHostAndPortRequestHandlerTestCase(tornado.testing.AsyncHTTPTestCase):

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
        delete_content_length = self.get_argument(
            "delete_content_length",
            False)
        if delete_content_length:
            del self.request.headers["Content-length"]
        response_body = self.get_request_body_if_exists(
            self.__class__.body_if_not_found)
        self.write(response_body)
        self.set_status(httplib.OK)


class GetRequestBodyIfExistsRequestHandlerTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        handlers = [(r".*", GetRequestBodyIfExistsRequestHandler), ]
        app = tornado.web.Application(handlers=handlers)
        return app

    def _do_it(self, body, expected_body, delete_content_length=False):
        query_string = ""
        if delete_content_length:
            query_string = "?delete_content_length=1"
        self.http_client.fetch(
            self.get_url(query_string),
            self.stop,
            method="POST",
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

    def test_no_content_length_header(self):
        body = ""
        self._do_it(
            body,
            GetRequestBodyIfExistsRequestHandler.body_if_not_found,
            delete_content_length=True)


class GetJSONRequestBodyRequestHandler(trhutil.RequestHandler):

    body_if_not_found = json.dumps({"uuid": _uuid()})

    def post(self):
        delete_content_length = self.get_argument(
            "delete_content_length",
            False)
        if delete_content_length:
            del self.request.headers["Content-length"]
        response_body = self.get_json_request_body(
            self.__class__.body_if_not_found)
        self.write(response_body)
        self.set_status(httplib.OK)


class GetJSONRequestBodyTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        handlers = [(r".*", GetJSONRequestBodyRequestHandler), ]
        app = tornado.web.Application(handlers=handlers)
        return app

    def _do_it(
        self,
        body,
        expected_body=None,
        content_type="application/json; charset=utf8",
        delete_content_length=False):

        query_string = ""
        if delete_content_length:
            query_string = "?delete_content_length=1"
        headers = {}
        if content_type is not None:
            headers["Content-type"] = content_type
        body = json.dumps(body)
        self.http_client.fetch(
            self.get_url(query_string),
            self.stop,
            method="POST",
            headers=tornado.httputil.HTTPHeaders(headers),
            body=body)
        response = self.wait()
        self.assertIsNotNone(response)
        self.assertEqual(response.code, httplib.OK)
        if expected_body is None:
            expected_body = body
        self.assertEqual(response.body, expected_body)

    def test_all_good_non_zero_length_body(self):
        body = {"dave": "was", "here": 42}
        self._do_it(body)

    def test_no_content_type(self):
        body = {"dave": "was", "here": 42}
        self._do_it(
            body,
            expected_body=GetJSONRequestBodyRequestHandler.body_if_not_found,
            content_type=None)

    def test_invalid_content_type(self):
        body = {"dave": "was", "here": 42}
        self._do_it(
            body,
            expected_body=GetJSONRequestBodyRequestHandler.body_if_not_found,
            content_type="dave")

class ResponseGetJSONBodyTestCase(unittest.TestCase):
    """A collection of unit tests to validate the behavior
    of ```trutil.Response.get_json_body()"""

    def _run_failure_scenario(self, response, value_if_not_found, schema=None):
        if value_if_not_found is None:
            self.assertIsNone(response.get_json_body(schema=schema))
        else:
            self.assertEqual(
                response.get_json_body(value_if_not_found, schema=schema),
                value_if_not_found)

    def _test_response_arg_is_none(self, value_if_not_found):
        response = trhutil.Response(None)

        self._run_failure_scenario(response, value_if_not_found)

    def test_response_arg_is_none_001(self):
        value_if_not_found = None
        self._test_response_arg_is_none(value_if_not_found)

    def test_response_arg_is_none_002(self):
        value_if_not_found = "dave"
        self._test_response_arg_is_none(value_if_not_found)

    def _test_response_code_is_not_ok(self, value_if_not_found):
        response_mock = mock.Mock()
        response_mock.code = httplib.INTERNAL_SERVER_ERROR
        response = trhutil.Response(response_mock)

        self._run_failure_scenario(response, value_if_not_found)

    def test_response_code_is_not_ok_001(self):
        value_if_not_found = None
        self._test_response_code_is_not_ok(value_if_not_found)

    def test_response_code_is_not_ok_002(self):
        value_if_not_found = "dave"
        self._test_response_code_is_not_ok(value_if_not_found)

    def _test_response_no_content_length_and_no_transfer_encoding(self, value_if_not_found):
        response_mock = mock.Mock()
        response_mock.code = httplib.OK
        response_mock.headers = {}
        response = trhutil.Response(response_mock)

        self._run_failure_scenario(response, value_if_not_found)

    def test_response_no_content_length_and_no_transfer_encoding_001(self):
        value_if_not_found = None
        self._test_response_no_content_length_and_no_transfer_encoding(value_if_not_found)

    def test_response_no_content_length_and_no_transfer_encoding_002(self):
        value_if_not_found = "dave"
        self._test_response_no_content_length_and_no_transfer_encoding(value_if_not_found)

    def _test_response_no_content_length_but_has_transfer_encoding(self, value_if_not_found):
        response_mock = mock.Mock()
        response_mock.code = httplib.OK
        response_mock.headers = {
            "Transfer-Encoding": "what goes here",
        }
        response = trhutil.Response(response_mock)

        self._run_failure_scenario(response, value_if_not_found)

    def test_response_no_content_length_but_has_transfer_encoding_001(self):
        value_if_not_found = None
        self._test_response_no_content_length_but_has_transfer_encoding(value_if_not_found)

    def test_response_no_content_length_but_has_transfer_encoding_002(self):
        value_if_not_found = None
        self._test_response_no_content_length_but_has_transfer_encoding(value_if_not_found)

    def _test_response_bad_content_type(self, value_if_not_found):
        response_mock = mock.Mock()
        response_mock.code = httplib.OK
        response_mock.headers = {
            "Content-length": 10,
            "Content-type": "bindle",
        }
        response = trhutil.Response(response_mock)

        self._run_failure_scenario(response, value_if_not_found)

    def test_response_bad_content_type_001(self):
        value_if_not_found = None
        self._test_response_bad_content_type(value_if_not_found)

    def test_response_bad_content_type_002(self):
        value_if_not_found = "dave"
        self._test_response_bad_content_type(value_if_not_found)

    # different json content types

    def _test_response_body_not_json(self, value_if_not_found):
        response_mock = mock.Mock()
        response_mock.code = httplib.OK
        response_mock.body = "dave"
        response_mock.headers = {
            "Content-length": len(response_mock.body),
            "Content-type": "application/json; charset=utf-8",
        }
        response = trhutil.Response(response_mock)

        self._run_failure_scenario(response, value_if_not_found)

    def test_response_body_not_json_001(self):
        value_if_not_found = None
        self._test_response_body_not_json(value_if_not_found)

    def test_response_body_not_json_002(self):
        value_if_not_found = "dave"
        self._test_response_body_not_json(value_if_not_found)

    def _test_response_body_jsonschmea_validation_failure(self, value_if_not_found):
        schema = {
            "type": "object",
            "properties": {
                "dave": {
                    "type": "boolean"
                },
            },
            "required": [
                "dave",
            ],
            "additionalProperties": False,
        }
        body = {
            "dave": "string that causes validation to fail"
        }
        response_mock = mock.Mock()
        response_mock.code = httplib.OK
        response_mock.body = json.dumps(body)
        response_mock.headers = {
            "Content-length": len(response_mock.body),
            "Content-type": "application/json; charset=utf-8",
        }
        response = trhutil.Response(response_mock)

        self._run_failure_scenario(response, value_if_not_found, schema)

    def test_response_body_jsonschmea_validation_failure_001(self):
         value_if_not_found = None
         self._test_response_body_jsonschmea_validation_failure(value_if_not_found)

    def test_response_body_jsonschmea_validation_failure_002(self):
         value_if_not_found = "dave"
         self._test_response_body_jsonschmea_validation_failure(value_if_not_found)

    def _test_response_ok_body(self, the_body, schema):
        response_mock = mock.Mock()
        response_mock.code = httplib.OK
        response_mock.body = json.dumps(the_body)
        response_mock.headers = {
            "Content-length": len(response_mock.body),
            "Content-type": "application/json; charset=utf-8",
        }
        response = trhutil.Response(response_mock)
        if schema is None:
            self.assertEqual(
                the_body,
                response.get_json_body())
        else:
            self.assertEqual(
                the_body,
                response.get_json_body(schema=schema))

    def test_response_ok_empty_body(self):
        body = {}
        schema = None
        self._test_response_ok_body(body, schema)

    def test_response_ok_something_in_body(self):
        body = {
            "dave": 1,
            "was": "here",
        }
        schema = None
        self._test_response_ok_body(body, schema)

    def test_response_ok_something_in_body_valid_against_schema(self):
        body = {
            "dave": True
        }
        schema = {
            "type": "object",
            "properties": {
                "dave": {
                    "type": "boolean"
                },
            },
            "required": [
                "dave",
            ],
            "additionalProperties": False,
        }
        self._test_response_ok_body(body, schema)
