"""This module contains functionality to async'ly create
credentials from the key store."""

import httplib
import logging
import uuid

from ks_util import filter_out_non_model_creds_properties
from ks_util import AsyncAction
from yar.util import mac
from yar.util import basic

_logger = logging.getLogger("KEYSERVICE.%s" % __name__)


class AsyncCredsCreator(AsyncAction):
    """```AsyncCredsCreator``` implements the async action
    pattern for creating credentials."""

    def create(self, principal, auth_scheme, callback):
        """Create a set of credentials for ```principal```,
        save the credentials to the key store and when all
        of that is done call ```callback``` with a single
        argument = the newly created credentials.

        If ```auth_scheme``` equals 'mac' credentials
        for an MAC authentication scheme are created otherwise
        credentials for basic authentication are created."""

        self._callback = callback

        self._creds = {
            "principal": principal,
            "type": "creds_v1.0",
            "is_deleted": False,
        }
        if auth_scheme == "mac":        
            self._creds["mac"] = {
                "mac_key_identifier": mac.MACKeyIdentifier.generate(),
                "mac_key": mac.MACKey.generate(),
                "mac_algorithm": mac.MAC.algorithm,
            }
        else:
            self._creds["basic"] = {
                "api_key": basic.APIKey.generate(),
            }

        self.async_req_to_key_store(
            "",
            "POST",
            self._creds,
            self._on_async_req_to_key_store_done)

    def _on_async_req_to_key_store_done(self, is_ok, code=None, body=None):
        """Called when async_req_to_key_store() completes."""

        if not is_ok or code != httplib.CREATED:
            self._callback(None)
            return

        creds = filter_out_non_model_creds_properties(self._creds)
        self._callback(creds)
