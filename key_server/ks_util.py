"""This module contains a collection of key server specific utilities."""

import json
import logging

import tornado.httpclient


_logger = logging.getLogger("KEYSERVER.%s" % __name__)


def _filter_out_non_model_creds_properties(creds):
    """When a dictionary representing a set of credentials
    is created, the dictionary may contain entries that are
    no part of the externally exposed model. This function
    takes a dictionary (```dict```), selects only the
    model properties in ```dict``` and returns a new
    dictionary containing only the model properties."""
    rv = {}
    keys = [
        "is_deleted",
        "mac_algorithm",
        "mac_key",
        "mac_key_identifier",
        "owner"
    ]
    for key in keys:
        if key in creds:
            rv[key] = creds[key]
    return rv


class AsyncAction(object):

    def __init__(self, key_store):
        object.__init__(self)
        self.key_store = key_store

    def issue_async_http_request_to_key_store(self, url, method, body, callback):
        json_encoded_body = json.dumps(body) if body else None
        headers = {
            "Content-Type": "application/json; charset=utf8",
            "Accept": "application/json",
            "Accept-Encoding": "charset=utf8"
        }
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(
            tornado.httpclient.HTTPRequest(
                url,
                method=method,
                headers=tornado.httputil.HTTPHeaders(headers),
                body=json_encoded_body),
            callback=callback)
