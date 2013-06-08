#!/usr/bin/env python
"""This module contains the core logic for the authenication server.
The server uses implements MAC Access Authentication."""

import logging
import re
import json
import httplib
import hashlib

import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web
import jsonschemas

from clparser import CommandLineParser
import async_creds_retriever
import async_nonce_checker
import tsh
import trhutil
import strutil
import mac


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

"""To help prevent reply attacks the timestamp of all requests can
be no older than ```maxage``` seconds before the current timestamp."""
maxage = 30

"""There are a billion ways in which authorization can fail. When
writing tests you want to know and should now in detail why things
fail but when running in production mode this detailed info should
not be returned to the caller. This switch controls if the HTTP
header X-AUTH-SERVER-AUTH-FAILURE-DETAIL is included in the server's
response when authorization fails."""
include_auth_failure_detail = False

# these constants define detailed authorization failure reasons
AUTH_FAILURE_DETAIL_TS_IN_FUTURE = str(0x0001)
AUTH_FAILURE_DETAIL_TS_OLD = str(0x0002)
AUTH_FAILURE_DETAIL_NO_AUTH_HEADER = str(0x0003)
AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER = str(0x0004)
AUTH_FAILURE_DETAIL_CREDS_NOT_FOUND = str(0x0005)
AUTH_FAILURE_DETAIL_NONCE_REUSED = str(0x0006)


class RequestHandler(trhutil.RequestHandler):

    def _set_debug_header(self, name, value):
        """Called by ```_set_debug_headers()``` to actually
        set the HTTP header called ```name``` of ```value```.
        This method is entirely about making the implementation
        of ```_set_debug_headers()``` cleaner."""
        name = "X-AUTH-SERVER-%s" % name
        value = strutil.make_http_header_value_friendly(value)
        self.set_header(name, value)

    def _set_auth_failure_detail(self, detail):
        """For details on this method see the comments associated with
        declaration of the include_auth_failure_detail global."""
        if include_auth_failure_detail:
            self.set_header("X-AUTH-SERVER-AUTH-FAILURE-DETAIL", detail)

    def _on_app_server_done(self, response):
        if response.error:
            self.set_status(httplib.INTERNAL_SERVER_ERROR)
        else:
            self.set_status(response.code)
            for header_name in response.headers.keys():
                self.set_header(header_name, response.headers[header_name])
            if 0 < response.headers.get("Content-Length", 0):
                self.write(response.body)
        self.finish()

    def _on_async_creds_retriever_done(
        self,
        is_ok,
        mac_key_identifier,
        is_deleted=None,
        mac_algorithm=None,
        mac_key=None,
        owner=None):

        if not is_ok:
            _logger.info(
                "No MAC credentials found for '%s'",
                self.request.full_url())
            self._set_auth_failure_detail(AUTH_FAILURE_DETAIL_CREDS_NOT_FOUND)
            self.set_status(httplib.UNAUTHORIZED)
            self.finish()
            return

        (host, port) = self.get_request_host_and_port("localhost", 80)
        content_type = self.request.headers.get("Content-type", None)
        body = self.get_request_body_if_exists(None)
        ext = mac.Ext.generate(content_type, body)
        normalized_request_string = mac.NormalizedRequestString.generate(
            self._auth_hdr_val.ts,
            self._auth_hdr_val.nonce,
            self.request.method,
            self.request.uri,
            host,
            port,
            ext)

        macs_equal = self._auth_hdr_val.mac.verify(
            mac_key,
            mac_algorithm,
            normalized_request_string)
        if not macs_equal:
            fmt = (
                "For '%s' using MAC key identifier '%s' "
                "MAC in request '%s' doesn't match computed MAC"
            )
            _logger.info(
                fmt,
                self.request.full_url(),
                mac_key_identifier,
                self._auth_hdr_val.mac)
            # When an authorization failure occurs it can be super hard
            # to figure out the root cause of the error. This method is called
            # on authorization failure and, if logging is set to at least
            # debug, a whole series of HTTP headers are set to return the
            # core elements that are used to generate the HMAC.
            if _logger.isEnabledFor(logging.DEBUG):
                if body:
                    self._set_debug_header(
                        "BODY-SHA1",
                        hashlib.sha1(body).hexdigest())
                    self._set_debug_header(
                        "BODY-LEN",
                        len(body))
                    self._set_debug_header(
                        "BODY",
                        body)

                self._set_debug_header(
                    "MAC-KEY-IDENTIFIER",
                    mac_key_identifier)
                self._set_debug_header(
                    "MAC-KEY",
                    mac_key)
                self._set_debug_header(
                    "MAC-ALGORITHM",
                    mac_algorithm)
                self._set_debug_header(
                    "HOST",
                    host)
                self._set_debug_header(
                    "PORT",
                    port)
                self._set_debug_header(
                    "CONTENT-TYPE",
                    content_type)
                self._set_debug_header(
                    "REQUEST-METHOD",
                    self.request.method)
                self._set_debug_header(
                    "URI",
                    self.request.uri)
                self._set_debug_header(
                    "TIMESTAMP",
                    self._auth_hdr_val.ts)
                self._set_debug_header(
                    "NONCE",
                    self._auth_hdr_val.nonce)
                self._set_debug_header(
                    "EXT",
                    ext)
            # end of pumping out debug headers - returning to regular headers
            self.set_status(httplib.UNAUTHORIZED)
            self.finish()
            return

        _logger.info(
            "Authorization successful for '%s' and MAC '%s'",
            self.request.full_url(),
            self._auth_hdr_val.mac)

        headers = tornado.httputil.HTTPHeaders(self.request.headers)
        headers["Authorization"] = "%s %s %s" % (
            app_server_auth_method,
            owner,
            mac_key_identifier)

        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(
            tornado.httpclient.HTTPRequest(
                url="http://%s%s" % (app_server, self.request.uri),
                method=self.request.method,
                body=body,
                headers=headers,
                follow_redirects=False),
            callback=self._on_app_server_done)

    def _on_async_nonce_checker_done(self, is_ok):
        """this callback is invoked when AsyncNonceChecker has finished.
        ```is_ok``` will be ```True`` AsyncNonceChecker has confirmed that
         the curent request's nonce+mac_key_identifier pair hasn't been
        seen before."""
        if not is_ok:
            self._set_auth_failure_detail(AUTH_FAILURE_DETAIL_NONCE_REUSED)
            self.set_status(httplib.UNAUTHORIZED)
            self.finish()
            return

        # basic request looks good
        #
        # 1/ authentication header found and format is valid
        # 2/ timestamp is recent
        # 3/ nonce has not previous been used by the mac key identifier
        #
        # next steps is to retrieve the credentials associated with
        # the request's mac key identifier and confirm the request's
        # MAC is valid ie. final step in confirming the sender's identity
        acr = async_creds_retriever.AsyncCredsRetriever()
        acr.fetch(
            self._on_async_creds_retriever_done,
            self._auth_hdr_val.mac_key_identifier)


    def _handle_request(self):
        """```get()```, ```post()```, ```put()``` & ```delete()```
        requests are all forwarded to this method which is
        responsible for kicking off the core authentication logic."""
        auth_hdr_val = self.request.headers.get("Authorization", None)
        if auth_hdr_val is None:
            self._set_auth_failure_detail(AUTH_FAILURE_DETAIL_NO_AUTH_HEADER)
            self.set_status(httplib.UNAUTHORIZED)
            self.finish()
            return

        self._auth_hdr_val = mac.AuthHeaderValue.parse(auth_hdr_val)
        if self._auth_hdr_val is None:
            self._set_auth_failure_detail(
                AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER)
            self.set_status(httplib.UNAUTHORIZED)
            self.finish()
            return

        # confirm the request isn't old which is important in protecting
        # against reply attacks - also requests with timestamps in the
        # future are also
        now = mac.Timestamp.generate()
        age = int(now) - int(self._auth_hdr_val.ts)
        if age < 0:
            # :TODO: timestamp in the future - bad - clocks out of sync?
            # do we want to allow clocks to be a wee bit ouf of sync?
            self._set_auth_failure_detail(AUTH_FAILURE_DETAIL_TS_IN_FUTURE)
            self.set_status(httplib.UNAUTHORIZED)
            self.finish()
            return

        if maxage < age:
            self._set_auth_failure_detail(AUTH_FAILURE_DETAIL_TS_OLD)
            self.set_status(httplib.UNAUTHORIZED)
            self.finish()
            return

        # time to confirm if the nonce in the request has been used
        # before. this means async'ly calling out to the memcached
        # cluster which stores previously used nonce+mac_key_identifer
        # combinations
        anc = async_nonce_checker.AsyncNonceChecker()
        anc.fetch(
            self._on_async_nonce_checker_done,
            self._auth_hdr_val.mac_key_identifier,
            self._auth_hdr_val.nonce)

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

    async_creds_retriever.key_server = clo.key_server
    app_server = clo.app_server
    auth_method = clo.app_server_auth_method
    maxage = clo.maxage
    async_nonce_checker.nonce_store = clo.nonce_store

    http_server = tornado.httpserver.HTTPServer(_app)
    http_server.listen(clo.port)
    tornado.ioloop.IOLoop.instance().start()
