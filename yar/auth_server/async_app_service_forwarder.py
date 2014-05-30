"""This module contains the logic for async forwarding
of requests to the app service."""

import logging

import tornado.httputil
import tornado.httpclient

from yar.util.trhutil import get_request_body_if_exists

_logger = logging.getLogger("AUTHSERVER.%s" % __name__)

"""Once a request has been authenticated, the request is forwarded
to the app service as defined by this host:port combination."""
app_service = None

"""Once the auth service has verified the sender's identity the request
is forwarded to the app service. The forward to the app service does not
contain the original request's HTTP Authorization header but instead
uses the authorization method described by ```app_service_auth_method```
and the the credential's principal."""
app_service_auth_method = "YAR"


class AsyncAppServiceForwarder(object):

    def __init__(self, method, uri, headers, body, principal):
        object.__init__(self)
        self._method = method
        self._uri = uri
        self._headers = headers
        self._body = body
        self._principal = principal

    def forward(self, callback):

        self._callback = callback

        headers = tornado.httputil.HTTPHeaders(self._headers)
        headers["Authorization"] = "%s %s" % (
            app_service_auth_method,
            self._principal)

        http_request = tornado.httpclient.HTTPRequest(
            url="http://%s%s" % (app_service, self._uri),
            method=self._method,
            body=self._body,
            headers=headers,
            follow_redirects=False)

        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(http_request, self._on_forward_done)

    def _on_forward_done(self, response):

        _logger.info("App Service (%s - %s) responded in %d ms",
            response.effective_url,
            response.request.method,
            int(response.request_time * 1000))

        if response.error:
            self._callback(False)
            return

        content_length = response.headers.get("Content-Length", -1)
        body = response.body if 0 <= content_length else None

        self._callback(True, response.code, response.headers, body)
