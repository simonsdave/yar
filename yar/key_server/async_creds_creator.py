"""This module contains functionality to async'ly create
credentials from the key store."""

import httplib
import logging
import uuid

from ks_util import filter_out_non_model_creds_properties
from ks_util import AsyncAction
from yar import mac

_logger = logging.getLogger("KEYSERVER.%s" % __name__)


class AsyncCredsCreator(AsyncAction):
    """```AsyncCredsCreator``` implements the async action
    pattern for creating credentials."""

    def create(self, owner, auth_scheme, callback):
        """Create a set of credentials for ```owner```,
        save the credentials to the key store and when all
        of that is done call ```callback``` with a single
        argument = the newly created credentials.

        If ```auth_scheme``` equals 'hmac' credentials
        for an HMAC authentication scheme are created otherwise
        credentials for basic authentication are created."""

        self._callback = callback

        self._creds = {
            "owner": owner,
            "type": "creds_v1.0",
            "is_deleted": False,
        }
        if auth_scheme == "hmac":        
            mac_key_identifier = mac.MACKeyIdentifier.generate()
            self._creds["hmac"] = {
                "mac_key_identifier": mac_key_identifier,
                "mac_key": mac.MACKey.generate(),
                "mac_algorithm": mac.MAC.algorithm,
            }
            path = mac_key_identifier
        else:
            # :TODO: need basic.APIKey.generate() instead of line below
            api_key = str(uuid.uuid4()).replace("-", "")
            self._creds["basic"] = {
                "api_key": api_key,
            }
            path = api_key

        self.async_req_to_key_store(
            path,
            "PUT",
            self._creds,
            self._on_async_req_to_key_store_done)

    def _on_async_req_to_key_store_done(self, is_ok, code=None, body=None):
        if not is_ok or code != httplib.CREATED:
            self._callback(None)
            return

        creds = filter_out_non_model_creds_properties(self._creds)
        self._callback(creds)
