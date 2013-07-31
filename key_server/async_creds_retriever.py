"""This module contains functionality to async'ly retrieve
credentials from the key store."""

import logging

from ks_util import _filter_out_non_model_creds_properties
from ks_util import AsyncAction


_logger = logging.getLogger("KEYSERVER.%s" % __name__)


class AsyncCredsRetriever(AsyncAction):

    def fetch(
        self,
        callback,
        mac_key_identifier=None,
        owner=None,
        is_filter_out_deleted=True,
        is_filter_out_non_model_properties=False):

        self._callback = callback
        self._is_filter_out_non_model_properties = \
            is_filter_out_non_model_properties
        self._is_filter_out_deleted = is_filter_out_deleted

        if mac_key_identifier:
            path = mac_key_identifier
        else:
            if owner:
                fmt = (
                    '_design/creds/_view/by_owner?'
                    'startkey="%s"'
                    '&'
                    'endkey="%s"'
                )
                path = fmt % (owner, owner)
            else:
                path = "_design/creds/_view/all"

        self.async_req_to_key_store(
            path,
            "GET",
            None,
            self._my_callback)

    def _my_callback(self, code, body):
        if not body:
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
                    doc = _filter_out_non_model_creds_properties(doc)
                rv.append(doc)
        else:
            is_creds_collection = False
            if body.get("is_deleted", False) and self._is_filter_out_deleted:
                rv = None
            else:
                if self._is_filter_out_non_model_properties:
                    body = _filter_out_non_model_creds_properties(body)
                rv = body
        assert is_creds_collection is not None

        self._callback(rv, is_creds_collection)
