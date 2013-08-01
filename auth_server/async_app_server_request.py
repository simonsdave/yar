#!/usr/bin/env python
"""This module contains the logic for async forwarding
of requests to the app server."""

import logging

import tornado.httputil
import tornado.httpclient

from trhutil import get_request_body_if_exists
"""
import httplib

import tornado.httpserver
import tornado.web

import strutil
import tsh

import async_creds_retriever
import async_nonce_checker
import async_hmac_auth
from clparser import CommandLineParser
"""

_logger = logging.getLogger("AUTHSERVER.%s" % __name__)


__version__ = "1.0"


"""Once a request has been authenticated, the request is forwarded
to the app server as defined by this host:port combination."""
app_server = None

"""Once the auth server has verified the sender's identity the request
is forwarded to the app server. The forward to the app server does not
contain the original request's HTTP Authorization header but instead
uses the authorization method described by ```app_server_auth_method```
and the the credential's owner."""
app_server_auth_method = "DAS"


class AsyncAppServerRequest(object):

    def _on_forward_done(self, response):
        if response.error:
            self._callback(False)
        else:
            body = None
            if 0 <= response.headers.get("Content-Length", 0):
                body = response.body 
            self._callback(
                True,
                response.code,
                response.headers,
                body)

    def forward(
        self,
        request,
        owner,
        identifier,
        callback):

        self._callback = callback

        headers = tornado.httputil.HTTPHeaders(request.headers)
        headers["Authorization"] = "%s %s %s" % (
            app_server_auth_method,
            owner,
            identifier)

        http_request = tornado.httpclient.HTTPRequest(
            url="http://%s%s" % (app_server, request.uri),
            method=request.method,
            body=get_request_body_if_exists(request),
            headers=headers,
            follow_redirects=False)

        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(
            http_request,
            callback=self._on_forward_done)
