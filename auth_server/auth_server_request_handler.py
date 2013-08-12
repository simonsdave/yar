#!/usr/bin/env python
"""This module contains the core logic for the authenication server.
The server uses implements MAC Access Authentication."""

import httplib
import logging

import tornado.web

import strutil
import trhutil

import async_hmac_auth
import async_app_server_forwarder

_logger = logging.getLogger("AUTHSERVER.%s" % __name__)

"""When authentication fails and the auth server's logging is set
to a debug level responses will contain a series of HTTP headers
that provide additional detail on why the authentication failed.
All of theses header names are prefixed by the value of
```debug_header_prefix```.""" 
debug_header_prefix = "X-Auth-Server-"

auth_failure_detail_header_name = "%sAuth-Failure-Detail" % debug_header_prefix

class RequestHandler(trhutil.RequestHandler):

    def _on_app_server_done(
        self,
        is_ok,
        http_status_code=None,
        headers=None,
        body=None):

        if not is_ok:
            self.set_status(httplib.INTERNAL_SERVER_ERROR)
        else:
            self.set_status(http_status_code)
            for (name, value) in headers.items():
                self.set_header(name, value)
            if body is not None:
                self.write(body)
        self.finish()

    def _on_auth_done(
        self,
        is_auth_ok,
        auth_failure_detail=None,
        auth_failure_debug_details=None,
        owner=None,
        identifier=None):

        if not is_auth_ok:

            self.set_status(httplib.UNAUTHORIZED)

            if auth_failure_detail:
                self.set_header(
                    auth_failure_detail_header_name,
                    auth_failure_detail)

            if auth_failure_debug_details:
                for (name, value) in auth_failure_debug_details.items():
                    name = "%s%s" % (debug_header_prefix, name)
                    value = strutil.make_http_header_value_friendly(value)
                    self.set_header(name, value)

            self.finish()
            
            return

        aasf = async_app_server_forwarder.AsyncAppServerForwarder(
            self.request.method,
            self.request.uri,
            self.request.headers,
            self.get_request_body_if_exists(),
            owner,
            identifier)
        aasf.forward(self._on_app_server_done)

    def _handle_request(self):
        gen_auth_failure_debug_details = _logger.isEnabledFor(logging.DEBUG)
        aha = async_hmac_auth.AsyncHMACAuth(
            self.request,
            gen_auth_failure_debug_details)
        aha.authenticate(self._on_auth_done)

    @tornado.web.asynchronous
    def get(self):
        self._handle_request()

    @tornado.web.asynchronous
    def post(self):
        self._handle_request()

    @tornado.web.asynchronous
    def put(self):
        self._handle_request()

    @tornado.web.asynchronous
    def delete(self):
        self._handle_request()
