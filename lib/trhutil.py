"""This module contains a series of utilities for writing
Tornado request handlers."""


import httplib
import re
import json
import uuid
import logging

import tornado.web
import jsonschema


def _is_json_content_type(content_type):
    """Returns True if ```content_type``` is a valid json
    content type otherwise returns False."""
    if content_type is None:
        return False
    json_content_type_reg_ex = re.compile(
        "^\s*application/json\s*$",
        re.IGNORECASE)
    if not json_content_type_reg_ex.match(content_type):
        return False
    return True


def _is_json_utf8_content_type(content_type):
    """Returns True if ```content_type``` is a valid utf8 json
    content type otherwise returns False."""
    if content_type is None:
        return False
    json_utf8_content_type_reg_ex = re.compile(
        "^\s*application/json;\s+charset\=utf-{0,1}8\s*$",
        re.IGNORECASE)
    if not json_utf8_content_type_reg_ex.match(content_type):
        return False
    return True


def get_request_host_and_port(
    request,
    host_if_not_found=None,
    port_if_not_found=None):
    """Return the request's 'Host' HTTP header parsed into its
    host and port components."""
    value = request.headers.get("Host", None)
    if value is None:
        return (host_if_not_found, port_if_not_found)

    reg_ex_pattern = r"^\s*(?P<host>[^\:]+)(?:\:(?P<port>\d+))?\s*$"
    reg_ex = re.compile(reg_ex_pattern)
    match = reg_ex.match(value)
    if not match:
        return (host_if_not_found, port_if_not_found)

    assert 0 == match.start()
    assert len(value) == match.end()
    num_matches = len(match.groups())
    assert (1 == num_matches) or (2 == num_matches)

    host = match.group("host")
    assert host
    assert 0 < len(host)

    port = match.group("port")
    if port is None:
        port = port_if_not_found

    return (host, port)


def get_request_body_if_exists(request, value_if_not_found=None):
    """Return the request's body if one exists otherwise
    return ```value_if_not_found```."""
    content_length = request.headers.get("Content-Length", None)
    if content_length is None:
        transfer_encoding = request.headers.get(
            "Transfer-Encoding",
            None)
        if transfer_encoding is None:
            return value_if_not_found
    if request.body is None:
        return value_if_not_found
    return request.body


class RequestHandler(tornado.web.RequestHandler):
    """When a request handler uses this as its base class rather than
    tornado.web.RequestHandler the request handler gains access to
    a collection of useful utility methods that operate on requests
    and responses. The utility methods focus on requests and responses
    that use JSON."""

    def get_request_host_and_port(
        self,
        host_if_not_found=None,
        port_if_not_found=None):
        """Return the request's 'Host' HTTP header parsed into its
        host and port components."""
        rv = get_request_host_and_port(
            self.request, 
            host_if_not_found,
            port_if_not_found)
        return rv

    def get_request_body_if_exists(self, value_if_not_found=None):
        """Return the request's body if one exists otherwise
        return ```value_if_not_found```."""
        rv = get_request_body_if_exists(
            self.request,
            value_if_not_found)
        return rv

    def get_json_request_body(self, value_if_not_found=None, schema=None):
        """Get the request's JSON body and convert it into a dict.
        If there's no body, the body isn't JSON, etc then return
        ```value_if_not_found``  otherwise return the dict.
        If ```schema``` is not None the JSON body is also validated
        against that jsonschema."""
        body = self.get_request_body_if_exists(None)
        if body is None:
            return value_if_not_found

        content_type = self.request.headers.get("content-type", None)
        if not _is_json_utf8_content_type(content_type):
            return value_if_not_found

        try:
            body = json.loads(body)
        except:
            return value_if_not_found

        if schema:
            try:
                jsonschema.validate(body, schema)
            except Exception as ex:
                return value_if_not_found

        return body


class Response(object):
    """A wrapper for a ```tornado.httpclient.HTTPResponse``` that exposes
    a number of useful, commonly used methods."""

    def __init__(self, response):
        object.__init__(self)
        self._response = response

    def get_json_body(self, value_if_not_found=None, schema=None):
        """Extract and return the JSON document from a
        ```tornado.httpclient.HTTPResponse``` as well as optionally
        validating the document against a schema. If there's
        an error along the way return None."""
        if self._response is None:
            return value_if_not_found

        if httplib.OK != self._response.code:
            return value_if_not_found

        content_length = self._response.headers.get("Content-length", 0)
        if 0 == content_length:
            transfer_encoding = self._response.headers.get(
                "Transfer-Encoding",
                None)
            if transfer_encoding is None:
                return value_if_not_found

        content_type = self._response.headers.get("Content-type", None)
        if not _is_json_utf8_content_type(content_type):
            if not _is_json_content_type(content_type):
                return value_if_not_found

        try:
            body = json.loads(self._response.body)
        except:
            return value_if_not_found

        if schema:
            try:
                jsonschema.validate(body, schema)
            except Exception as ex:
                return value_if_not_found

        return body
