"""This module contains functionality to async'ly delete
credentials from the key store."""

import httplib
import logging

from async_creds_retriever import AsyncCredsRetriever
from ks_util import AsyncAction

_logger = logging.getLogger("KEYSERVICE.%s" % __name__)


class AsyncCredsDeleter(AsyncAction):

    def delete(self, key, callback):
        self._callback = callback

        acr = AsyncCredsRetriever(self.key_store)
        acr.fetch(
            self._on_async_creds_retriever_done,
            key=key,
            is_filter_out_deleted=False)

    def _on_async_creds_retriever_done(self, creds, is_creds_collection):
        if creds is None:
            self._callback(False)
            return

        assert not is_creds_collection

        if creds.get("is_deleted", False):
            self._callback(True)
            return

        creds["is_deleted"] = True

        self.async_req_to_key_store(
            creds["mac_key_identifier"],
            "PUT",
            creds,
            self._on_response_from_key_store_to_put_for_delete)

    def _on_response_from_key_store_to_put_for_delete(self, is_ok, code=None, body=None):
        self._callback(is_ok and code == httplib.CREATED)
