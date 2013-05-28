"""This module hides the gory details of async'ly interacting
with the key store to retrieve credentials."""

import httplib
import logging

import jsonschemas
import tornado.httpclient

import mac
import trhutil

__version__ = "1.0"

_logger = logging.getLogger("AUTHSERVER.%s" % __name__)

"""This host:port combination define the location of the key server."""
key_server = None


class AsyncCredsRetriever(object):
    """Wraps the gory details of async crednetials retrieval."""

    def fetch(self, callback, mac_key_identifier):
        """Retrieve the credentials for ```mac_key_identifier```
        and when done call ```callback```."""

        self._callback = callback
        self._mac_key_identifier = mac_key_identifier

        url = "http://%s/v1.0/creds/%s" % (
            key_server,
            self._mac_key_identifier)
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(
            tornado.httpclient.HTTPRequest(
                url=url,
                method="GET",
                follow_redirects=False),
            callback=self._my_callback)

    def _my_callback(self, response):
        """Called when request to the key server returns."""
        if response.code != httplib.OK:
            self._callback(False, self._mac_key_identifier)
            return

        response = trhutil.Response(response)
        body = response.get_json_body(
            jsonschemas.key_server_get_creds_response)
        if body is None:
            self._callback(False, self._mac_key_identifier)
            return

        _logger.info(
            "For mac key identifier '%s' retrieved credentials '%s'",
            self._mac_key_identifier,
            body)

        self._callback(
            True,
            mac.MACKeyIdentifier(self._mac_key_identifier),
            body["is_deleted"],
            body["mac_algorithm"],
            mac.MACKey(body["mac_key"]),
            body["owner"])
