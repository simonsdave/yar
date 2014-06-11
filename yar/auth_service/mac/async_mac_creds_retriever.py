"""This module hides the gory details of async'ly interacting
with the key service to retrieve credentials."""

import httplib
import logging

import tornado.httpclient

from yar.key_service import jsonschemas
from yar.util import mac
from yar.util import trhutil

_logger = logging.getLogger("AUTHSERVICE.%s" % __name__)

"""This host:port combination define the location of the key service."""
key_service_address = "127.0.0.1:8070"


class AsyncMACCredsRetriever(object):
    """Wraps the gory details of async crednetials retrieval."""

    def __init__(self, mac_key_identifier):
        object.__init__(self)
        self._mac_key_identifier = mac_key_identifier

    def fetch(self, callback):
        """Retrieve the credentials for ```mac_key_identifier```
        and when done call ```callback```."""

        self._callback = callback

        url = "http://%s/v1.0/creds/%s" % (
            key_service_address,
            self._mac_key_identifier)
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

        if response.error or response.code != httplib.OK:
            self._callback(False, self._mac_key_identifier)
            return

        body = trhutil.get_json_body_from_response(
            response,
            None,
            jsonschemas.get_creds_response)
        if body is None:
            self._callback(False, self._mac_key_identifier)
            return

        _logger.info(
            "For mac key identifier '%s' retrieved credentials '%s'",
            self._mac_key_identifier,
            body)

        self._callback(
            True,
            mac.MACKeyIdentifier(body["mac"]["mac_key_identifier"]),
            body["is_deleted"],
            body["mac"]["mac_algorithm"],
            mac.MACKey(body["mac"]["mac_key"]),
            body["principal"])
