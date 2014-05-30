"""This module hides the gory details of async'ly interacting
with the key service to retrieve credentials for the basic
authentication scheme."""

import httplib
import logging

import tornado.httpclient

from yar.key_service import jsonschemas
from yar.util import mac
from yar.util import trhutil

_logger = logging.getLogger("AUTHSERVER.%s" % __name__)

"""This host:port combination define the location of the key service."""
key_service = "127.0.0.1:8070"


class AsyncCredsRetriever(object):
    """Wraps all the gory details of async'ly interacting with
    the key service to retrieve credentials for use with basic
    authentication scheme."""

    def __init__(self, api_key):
        object.__init__(self)
        self._api_key = api_key

    def fetch(self, callback):
        """Retrieve the credentials for ```self._api_key```
        and when done call ```callback```."""

        self._callback = callback

        url = "http://%s/v1.0/creds/%s" % (
            key_service_address,
            self._api_key)
        http_request = tornado.httpclient.HTTPRequest(
            url=url,
            method="GET",
            follow_redirects=False)
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(http_request, self._on_fetch_done)

    def _on_fetch_done(self, response):
        """Called when request to the key service returns."""

        _logger.info("Key Service (%s - %s) responded in %d ms",
            response.effective_url,
            response.request.method,
            int(response.request_time * 1000))

        expected_response_codes = [
            httplib.OK,
            httplib.NOT_FOUND,
        ]
        if response.error or response.code not in expected_response_codes:
            self._callback(False)
            return

        if response.code == httplib.NOT_FOUND:
            self._callback(True, None)
            return

        response = trhutil.Response(response)
        body = response.get_json_body(schema=jsonschemas.get_creds_response)
        if body is None:
            self._callback(False)
            return

        _logger.info(
            "Successfully retrieved basic auth credentials for api key '%s'",
            self._api_key)

        self._callback(True, body["principal"])
