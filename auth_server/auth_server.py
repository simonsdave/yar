#!/usr/bin/env python
"""This module contains the core logic for the authenication server.
The server uses implements MAC Access Authentication."""

import httplib
import logging

import tornado.httpserver
import tornado.web

import strutil
import trhutil
import tsh

import async_creds_retriever
import async_nonce_checker
import async_hmac_auth
from clparser import CommandLineParser


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

"""When authentication fails and the auth server's logging is set
to a debug level responses will contain a series of HTTP headers
that provide additional detail on why the authentication failed.
All of theses header names are prefixed by the value of
```debug_header_prefix```.""" 
debug_header_prefix = "X-Auth-Server-"

"""```True``` if debug headers should be generated by the async
authentication classes and included in response to requests
that fail authentication."""
generate_debug_headers = False

class RequestHandler(trhutil.RequestHandler):

    def _on_app_server_done(self, response):
        if response.error:
            self.set_status(httplib.INTERNAL_SERVER_ERROR)
        else:
            self.set_status(response.code)
            for (name, value) in response.headers.items():
                self.set_header(name, value)
            if 0 < response.headers.get("Content-Length", 0):
                self.write(response.body)
        self.finish()

    def _on_auth_done(
        self,
        is_auth_ok,
        auth_failure_detail=None,
        debug_headers=None,
        owner=None,
        identifying_key=None):

        if not is_auth_ok:

            self.set_status(httplib.UNAUTHORIZED)

            if auth_failure_detail:
                self.set_header(
                    "%sAuth-Failure-Detail" % debug_header_prefix,
                    auth_failure_detail)

            if debug_headers:
                for (name, value) in debug_headers.items():
                    name = "%s%s" % (debug_header_prefix, name)
                    value = strutil.make_http_header_value_friendly(value)
                    self.set_header(name, value)

            self.finish()
            
            return

        #
        # milestone! request has just passed authorization:-)
        # next step is to forward the request to the application
        # server.
        #
        headers = tornado.httputil.HTTPHeaders(self.request.headers)
        headers["Authorization"] = "%s %s %s" % (
            app_server_auth_method,
            owner,
            identifying_key)

        http_request = tornado.httpclient.HTTPRequest(
            url="http://%s%s" % (app_server, self.request.uri),
            method=self.request.method,
            body=self.get_request_body_if_exists(),
            headers=headers,
            follow_redirects=False)

        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(
            http_request,
            callback=self._on_app_server_done)

    def _handle_request(self):
        aha = async_hmac_auth.AsyncHMACAuth(
            self.request,
            generate_debug_headers)
        aha.validate(self._on_auth_done)

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


_handlers = [(r".*", RequestHandler), ]
_app = tornado.web.Application(handlers=_handlers)


if __name__ == "__main__":
    clp = CommandLineParser()
    (clo, cla) = clp.parse_args()

    tsh.install_handler()

    logging.basicConfig(level=clo.logging_level)

    fmt = (
        "Auth Server listening on {clo.port} "
        "using Nonce Store {clo.nonce_store}, "
        "Key Server '{clo.app_server}' "
        "and App Server '{clo.app_server}'"
    )
    _logger.info(fmt.format(clo=clo))

    generate_debug_headers = _logger.isEnabledFor(logging.DEBUG)
    app_server = clo.app_server
    auth_method = clo.app_server_auth_method

    async_creds_retriever.key_server = clo.key_server
    async_hmac_auth.maxage = clo.maxage
    async_nonce_checker.nonce_store = clo.nonce_store

    http_server = tornado.httpserver.HTTPServer(_app)
    http_server.listen(clo.port)
    tornado.ioloop.IOLoop.instance().start()
