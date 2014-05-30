"""This module contains the core logic for the auth service."""

import httplib
import logging
import re

import tornado.web

import mac.async_mac_auth
import basic.async_auth
import async_app_service_forwarder
from yar.util import strutil
from yar.util import trhutil

_logger = logging.getLogger("AUTHSERVICE.%s" % __name__)

"""When authentication fails and the auth service's logging is set
to a debug level responses will contain a series of HTTP headers
that provide additional detail on why the authentication failed.
All of theses header names are prefixed by the value of
```debug_header_prefix```."""
debug_header_prefix = "X-Yar-Auth-"

auth_failure_detail_header_name = "%sAuth-Failure-Detail" % debug_header_prefix

# implementation of ```_include_auth_failure_debug_details()``` is pretty
# obvious. what might be less clear is the motivation for the function.
# this function is only here so that test frameworks can override the
# implementation to force and unforce auth debug details to be generated
def _include_auth_failure_debug_details():
    return _logger.isEnabledFor(logging.DEBUG)

# these constants define detailed authentication failure reasons
AUTH_FAILURE_DETAIL_NO_AUTH_HEADER = 0x0000 + 0x0001
AUTH_FAILURE_DETAIL_UNKNOWN_AUTHENTICATION_SCHEME = 0x0000 + 0x0002
AUTH_FAILURE_DETAIL_FOR_TESTING = 0x0000 + 0x00ff

"""When the auth service first recieves a request it extracts the
authentication scheme from the value associated with the request's 
HTTP authorization header. ```_auth_scheme_reg_ex``` is the regular
expression used to parse and extract the authentication scheme."""
_auth_scheme_reg_ex = re.compile(
    "^\s*(?P<auth_scheme>(MAC|BASIC))\s+.*",
    re.IGNORECASE)

"""The auth service supports a number of authentication mechanisms.
```_auth_scheme_to_auth_class``` is used to convert an authentication scheme
into the class that implements the authentication mechanism."""
_auth_scheme_to_auth_class = {
    "MAC": mac.async_mac_auth.AsyncMACAuth,
    "BASIC": basic.async_auth.Authenticator,
}

"""The auth service's mainline should use this URL spec
to describe the URLs that ```RequestHandler``` can
correctly service."""
url_spec = r".*"


class RequestHandler(trhutil.RequestHandler):

    #
    # :TODO: what happens to "custom" HTTP methods outside of the 
    # 7 method listed below?
    #

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

    @tornado.web.asynchronous
    def options(self):
        self._handle_request()

    @tornado.web.asynchronous
    def head(self):
        self._handle_request()

    @tornado.web.asynchronous
    def patch(self):
        self._handle_request()

    def _handle_request(self):
        auth_hdr_val = self.request.headers.get("Authorization", None)
        if auth_hdr_val is None:
            self._on_auth_done(
                is_auth_ok=False,
                auth_failure_detail=AUTH_FAILURE_DETAIL_NO_AUTH_HEADER)
            return

        match = _auth_scheme_reg_ex.match(auth_hdr_val)
        if not match:
            self._on_auth_done(
                is_auth_ok=False,
                auth_failure_detail=AUTH_FAILURE_DETAIL_UNKNOWN_AUTHENTICATION_SCHEME)
            return

        auth_scheme = match.group("auth_scheme")
        auth_class = _auth_scheme_to_auth_class.get(auth_scheme.upper(), None)
        # :TRICKY: assert works because _auth_scheme_reg_ex above
        # weeds out unsupported authentication types
        assert auth_class is not None

        aha = auth_class(self.request)
        aha.authenticate(self._on_auth_done)

    def _on_auth_done(
        self,
        is_auth_ok,
        auth_failure_detail=None,
        auth_failure_debug_details=None,
        principal=None):

        # :TODO: how to differentiate between an authentication failure
        # and a failure with the authentication infrastructure

        if not is_auth_ok:

            self.set_status(httplib.UNAUTHORIZED)

            if _include_auth_failure_debug_details():

                if auth_failure_detail:
                    self.set_header(
                        auth_failure_detail_header_name,
                        "0x{:04x}".format(auth_failure_detail))

                if auth_failure_debug_details:
                    for (name, value) in auth_failure_debug_details.items():
                        name = "%s%s" % (debug_header_prefix, name)
                        value = strutil.make_http_header_value_friendly(value)
                        self.set_header(name, value)

            self.finish()

            return

        # the request has been successfully authenticated:-)
        # all that's left now is to asyc'y forward the request 
        # to the app service
        aasf = async_app_service_forwarder.AsyncAppServiceForwarder(
            self.request.method,
            self.request.uri,
            self.request.headers,
            self.get_request_body_if_exists(),
            principal)
        aasf.forward(self._on_app_service_done)

    def _on_app_service_done(
        self,
        is_ok,
        http_status_code=None,
        headers=None,
        body=None):

        if is_ok:
            self.set_status(http_status_code)
            for (name, value) in headers.items():
                self.set_header(name, value)
            if body is not None:
                self.write(body)
        else:
            self.set_status(httplib.INTERNAL_SERVER_ERROR)

        self.finish()

    def set_default_headers(self):
        """The less a potential threat knows about security infrastructre
        the better. With that in mind, this method attempts to remove the
        Server HTTP header if it appears in a response. This won't
        protect against app service's returning such a header since yar
        just proxies the response but it will prevent this header from leaking
        out in scenarios such as authentocation failure because no
        Authorization header was found in the request."""
        self.clear_header("Server")
