"""This module contains functionality to async'ly retrieve
credentials from the key store."""

import httplib
import logging

from ks_util import filter_out_non_model_creds_properties
from ks_util import AsyncAction


_logger = logging.getLogger("KEYSERVER.%s" % __name__)


class AsyncCredsRetriever(AsyncAction):

    def fetch(
        self,
        callback,
        key=None,
        principal=None,
        is_filter_out_deleted=True,
        is_filter_out_non_model_properties=False):

        self._callback = callback
        self._is_filter_out_non_model_properties = \
            is_filter_out_non_model_properties
        self._is_filter_out_deleted = is_filter_out_deleted

        if key:
            path = key
        else:
            if principal:
                fmt = (
                    '_design/creds/_view/by_principal?'
                    'key="%s"'
                )
                path = fmt % principal
            else:
                path = "_design/creds/_view/all"

        self.async_req_to_key_store(
            path,
            "GET",
            None,
            self._my_callback)

    def _my_callback(self, is_ok, code=None, body=None):
        if not is_ok or httplib.OK != code or body is None:
            self._callback(None, None)
            return

        is_creds_collection = None
        if 'rows' in body:
            is_creds_collection = True
            rv = []
            for row in body['rows']:
                doc = row['value']
                if doc.get("is_deleted", False):
                    if self._is_filter_out_deleted:
                        continue
                if self._is_filter_out_non_model_properties:
                    doc = filter_out_non_model_creds_properties(doc)
                rv.append(doc)
        else:
            is_creds_collection = False
            if body.get("is_deleted", False) and self._is_filter_out_deleted:
                rv = None
            else:
                if self._is_filter_out_non_model_properties:
                    body = filter_out_non_model_creds_properties(body)
                rv = body
        assert is_creds_collection is not None

        self._callback(rv, is_creds_collection)
