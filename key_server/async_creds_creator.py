"""This module contains the core key server logic."""

import httplib
import json
import logging

import tornado.httpclient

import mac

from ks_util import _filter_out_non_model_creds_properties


_logger = logging.getLogger("KEYSERVER.%s" % __name__)


class AsyncCredsCreator(object):

    def __init__(self, key_store):
        object.__init__(self)
        self._key_store = key_store

    def create(self, owner, callback):

        self._callback = callback

        self._creds = {
            "owner": owner,
            "mac_key_identifier": mac.MACKeyIdentifier.generate(),
            "mac_key": mac.MACKey.generate(),
            "mac_algorithm": mac.MAC.algorithm,
            "type": "cred_v1.0",
            "is_deleted": False,
        }
        headers = {
            "Content-Type": "application/json; charset=utf8",
            "Accept": "application/json",
            "Accept-Encoding": "charset=utf8"
        }
        url = "http://%s/%s" % (
            self._key_store,
            self._creds["mac_key_identifier"])
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(
            tornado.httpclient.HTTPRequest(
                url,
                method="PUT",
                headers=tornado.httputil.HTTPHeaders(headers),
                body=json.dumps(self._creds)),
            callback=self._my_callback)

    def _my_callback(self, response):
        if response.code != httplib.CREATED:
            self._callback(None)
            return

        creds = _filter_out_non_model_creds_properties(self._creds)
        self._callback(creds)
