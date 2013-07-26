"""This module contains functionality to async'ly create
credentials from the key store."""

import httplib
import logging

import mac

from ks_util import _filter_out_non_model_creds_properties
from ks_util import AsyncAction


_logger = logging.getLogger("KEYSERVER.%s" % __name__)


class AsyncCredsCreator(AsyncAction):

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
        url = "http://%s/%s" % (
            self.key_store,
            self._creds["mac_key_identifier"])
        self.issue_async_http_request_to_key_store(
            url,
            "PUT",
            self._creds,
            self._my_callback)

    def _my_callback(self, response):
        if response.code != httplib.CREATED:
            self._callback(None)
            return

        creds = _filter_out_non_model_creds_properties(self._creds)
        self._callback(creds)
