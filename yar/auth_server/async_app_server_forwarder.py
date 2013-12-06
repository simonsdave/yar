#!/usr/bin/env python
"""This module contains the logic for async forwarding
of requests to the app server."""


import logging

import tornado.httputil
import tornado.httpclient

from yar.trhutil import get_request_body_if_exists


_logger = logging.getLogger("AUTHSERVER.%s" % __name__)


"""Once a request has been authenticated, the request is forwarded
to the app server as defined by this host:port combination."""
app_server = None

"""Once the auth server has verified the sender's identity the request
is forwarded to the app server. The forward to the app server does not
contain the original request's HTTP Authorization header but instead
uses the authorization method described by ```app_server_auth_method```
and the the credential's owner."""
app_server_auth_method = "DAS"


class AsyncAppServerForwarder(object):

    def __init__(self, method, uri, headers, body, owner, identifier):
        object.__init__(self)
        self._method = method
        self._uri = uri
        self._headers = headers
        self._body = body
        self._owner = owner
        self._identifier = identifier

    def forward(self, callback):

        self._callback = callback

        headers = tornado.httputil.HTTPHeaders(self._headers)
        headers["Authorization"] = "%s %s %s" % (
            app_server_auth_method,
            self._owner,
            self._identifier)

        http_request = tornado.httpclient.HTTPRequest(
            url="http://%s%s" % (app_server, self._uri),
            method=self._method,
            body=self._body,
            headers=headers,
            follow_redirects=False)

        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(
            http_request,
            self._on_forward_done)

    def _on_forward_done(self, response):
        if response.error:
            self._callback(False)
            return

        body = None
        if 0 <= response.headers.get("Content-Length", -1):
            body = response.body
        self._callback(
            True,
            response.code,
            response.headers,
            body)
