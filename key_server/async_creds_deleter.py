"""This module contains functionality to async'ly delete
credentials from the key store."""

import httplib
import json
import logging

from async_creds_retriever import AsyncCredsRetriever
from ks_util import AsyncAction


_logger = logging.getLogger("KEYSERVER.%s" % __name__)


class AsyncCredsDeleter(AsyncAction):

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

        url = "http://%s/%s" % (
            self.key_store,
            creds["mac_key_identifier"])
        self.issue_async_http_request_to_key_store(
            url,
            "PUT",
            creds,
            self._on_response_from_key_store_to_put_for_delete)

    def delete(self, mac_key_identifier, callback):
        self._callback = callback

        acr = AsyncCredsRetriever(self.key_store)
        acr.fetch(
            self._on_async_creds_retriever_done,
            mac_key_identifier=mac_key_identifier,
            is_filter_out_deleted=False)
