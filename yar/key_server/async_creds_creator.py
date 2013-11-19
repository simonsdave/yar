"""This module contains functionality to async'ly create
credentials from the key store."""

import httplib
import logging

from ks_util import filter_out_non_model_creds_properties
from ks_util import AsyncAction
from yar import mac


_logger = logging.getLogger("KEYSERVER.%s" % __name__)


class AsyncCredsCreator(AsyncAction):
    """```AsyncCredsCreator``` implements the async action
    pattern for creating MAC credentials."""

    def create(self, owner, callback):
        """Create a set of MAC credentials for ```owner```,
        save the credentials to the key store and when all
        of that is done call ```callback``` with a single
        argument = the newly created credentials."""

        self._callback = callback

        self._creds = {
            "owner": owner,
            "mac_key_identifier": mac.MACKeyIdentifier.generate(),
            "mac_key": mac.MACKey.generate(),
            "mac_algorithm": mac.MAC.algorithm,
            "type": "cred_v1.0",
            "is_deleted": False,
        }
        self.async_req_to_key_store(
            self._creds["mac_key_identifier"],
            "PUT",
            self._creds,
            self._my_callback)

    def _my_callback(self, is_ok, code=None, body=None):
        if not is_ok or code != httplib.CREATED:
            self._callback(None)
            return

        creds = filter_out_non_model_creds_properties(self._creds)
        self._callback(creds)
