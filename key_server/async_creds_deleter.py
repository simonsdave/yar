"""This module contains functionality to async'ly delete
credentials from the key store."""

import httplib
import json
import logging

import tornado.httpclient

from async_creds_retriever import AsyncCredsRetriever


_logger = logging.getLogger("KEYSERVER.%s" % __name__)


class AsyncCredsDeleter(object):

    def __init__(self, key_store):
        self._key_store = key_store

    def _on_response_from_key_store_to_put_for_delete(self, response):
        self._callback(response.code == httplib.CREATED)

    def _on_async_creds_retriever_done(self, creds, is_creds_collection):
        if creds is None:
            self._callback(False)
            return

        assert not is_creds_collection

        if creds.get("is_deleted", False):
            self._callback(True)
            return

        creds["is_deleted"] = True

        headers = {
            "Content-Type": "application/json; charset=utf8",
            "Accept": "application/json",
            "Accept-Encoding": "charset=utf8",
        }
        url = "http://%s/%s" % (
            self._key_store,
            creds["mac_key_identifier"])
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch(
            tornado.httpclient.HTTPRequest(
                url,
                method="PUT",
                headers=tornado.httputil.HTTPHeaders(headers),
                body=json.dumps(creds)),
            callback=self._on_response_from_key_store_to_put_for_delete)

    def delete(self, mac_key_identifier, callback):
        self._callback = callback

        acr = AsyncCredsRetriever(self._key_store)
        acr.fetch(
            self._on_async_creds_retriever_done,
            mac_key_identifier=mac_key_identifier,
            is_filter_out_deleted=False)
