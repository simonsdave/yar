"""This module contains a collection of key service specific utilities."""

import json
import logging

import tornado.httpclient

from yar.util import trhutil

_logger = logging.getLogger("KEYSERVICE.%s" % __name__)


def filter_out_non_model_creds_properties(creds):
    """When a dictionary representing a set of credentials
    is created, the dictionary may contain entries that are
    not part of the externally exposed model. This function
    takes a dictionary (```dict```), selects only the
    credential model properties in ```dict``` and returns
    a new dictionary containing only the model properties."""
    if creds is None:
        return None
    model_creds_properties = [
        "basic",
        "mac",
        "principal"
    ]
    return {k: v for k, v in creds.iteritems() if k in model_creds_properties}


class AsyncAction(object):
    """```AsyncAction``` is an abstract base class for all key
    service classes which encapsulate async interaction between
    the key service and key store. The primary intent of this
    class is to abstract away all tornado details from the
    derived classes and isolate the async control code into
    a single spot. This isolation makes mock creation in unit
    tests super easy."""

    def __init__(self, key_store):
        """```AsyncAction```'s constructor.
        ```key_store``` is expected to convert to a string
        of the form 'host:port'."""
        object.__init__(self)
        self.key_store = key_store

    def async_req_to_key_store(self,
                               path,
                               method,
                               body,
                               callback):

        self._my_callback = callback

        url = "http://%s/%s" % (self.key_store, path)

        json_encoded_body = json.dumps(body) if body else None

        headers = tornado.httputil.HTTPHeaders({
            "Accept": "application/json",
            "Accept-Encoding": "charset=utf8",
        })
        if body:
            headers["Content-Type"] = "application/json; charset=utf8"

        request = tornado.httpclient.HTTPRequest(
            url,
            method=method,
            headers=headers,
            body=json_encoded_body)

        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(
            request,
            callback=self._http_client_fetch_callback)

    def _http_client_fetch_callback(self, response):
        """Called when ```tornado.httpclient.AsyncHTTPClient``` completes."""

        """:TRICKY: Need to be careful about changing this message format
        because the load testing infrastructure scrapes the logs for this
        message in this format."""
        _logger.info(
            "Key Store (%s - %s) responded in %d ms",
            response.effective_url,
            response.request.method,
            int(response.request_time * 1000))

        if response.error:
            _logger.error(
                "Key Store responded to %s on %s with error '%s'",
                response.request.method,
                response.effective_url,
                response.error)

            self._my_callback(False)
            return

        self._my_callback(
            True,
            response.code,
            trhutil.get_json_body_from_response(response))
