"""This module contains functionality to async'ly retrieve
credentials from the key store."""

import httplib
import logging

from ks_util import filter_out_non_model_creds_properties
from ks_util import AsyncAction

_logger = logging.getLogger("KEYSERVICE.%s" % __name__)


class AsyncCredsRetriever(AsyncAction):

    def fetch(
        self,
        callback,
        key=None,
        principal=None,
        is_filter_out_deleted=True,
        is_filter_out_non_model_properties=False):

        self._key = key
        self._principal = principal
        self._callback = callback
        self._is_filter_out_non_model_properties = \
            is_filter_out_non_model_properties
        self._is_filter_out_deleted = is_filter_out_deleted

        if key:
            path = '_design/by_identifier/_view/by_identifier?key="%s"' % key
        else:
            path = '_design/by_principal/_view/by_principal?key="%s"' % principal

        self.async_req_to_key_store(
            path,
            "GET",
            None,
            self._on_async_req_to_key_store_done)

    def _on_async_req_to_key_store_done(self, is_ok, code=None, body=None):
        """Called when async_req_to_key_store() is done."""

        if not is_ok or httplib.OK != code or body is None:
            self._callback(None, None)
            return

        creds = []
        for row in body.get("rows", []):
            doc = row.get("value", {})
            if doc.get("is_deleted", False):
                if self._is_filter_out_deleted:
                    continue
            if self._is_filter_out_non_model_properties:
                doc = filter_out_non_model_creds_properties(doc)
            creds.append(doc)

        if self._key:
            # asked to retrive a single set of creds so
            # expecting 1 or 0 values in "creds"
            num_creds = len(creds)

            if 0 == num_creds:
                self._callback(None, False)
            else:
                if 1 == num_creds:
                    self._callback(creds[0], False)
                else:
                    self._callback(None, None)
        else:
            self._callback(creds, True)
