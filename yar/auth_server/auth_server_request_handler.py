"""This module contains the core logic for the authenication server.
The server uses implements MAC Access Authentication."""

import httplib
import logging
import re

import tornado.web

import hmac.async_hmac_auth
import async_app_server_forwarder
from yar.util import strutil
from yar.util import trhutil

_logger = logging.getLogger("AUTHSERVER.%s" % __name__)

"""```_gen_auth_failure_debug_details``` set to ```True```
when auth server should return auth debug details to the
caller. Should be really careful with this setting (ie.
don't run auth server in production environment) as it
will expose details of authentication scheme implementation
that could highlight vulnerabilities."""
_gen_auth_failure_debug_details = _logger.isEnabledFor(logging.DEBUG)

"""When authentication fails and the auth server's logging is set
to a debug level responses will contain a series of HTTP headers
that provide additional detail on why the authentication failed.
All of theses header names are prefixed by the value of
```debug_header_prefix```."""
debug_header_prefix = "X-Auth-Server-"

auth_failure_detail_header_name = "%sAuth-Failure-Detail" % debug_header_prefix

"""When the auth server first recieves a request it extracts the
authentication scheme from the value associated with the request's 
HTTP authorization header. ```_auth_scheme_reg_ex``` is the regular
expression used to parse and extract the authentication scheme."""
_auth_scheme_reg_ex = re.compile(
    "^\s*(?P<auth_scheme>(MAC|BASIC))\s+.*",
    re.IGNORECASE)

"""The authentication server supports a number of authentication mechanisms.
```_auth_scheme_to_auth_class``` is used to convert an authentication scheme
into the class that implements the authentication mechanism."""
_auth_scheme_to_auth_class = {
    "MAC": hmac.async_hmac_auth.AsyncHMACAuth,
}


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
        auth_hdr_val = self.request.headers.get("Authorization", None)
        if not auth_hdr_val:
            self._on_auth_done(False)
            return

        match = _auth_scheme_reg_ex.match(auth_hdr_val)
        if not match:
            self._on_auth_done(False)
            return

        auth_scheme = match.group("auth_scheme")

        auth_class = _auth_scheme_to_auth_class.get(auth_scheme.upper(), None)
        if not auth_class:
            self._on_auth_done(False)
            return

        aha = auth_class(
            self.request,
            _gen_auth_failure_debug_details)
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
