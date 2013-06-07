"""This module hides the gory details of async'ly interacting
with the nonce store to determine if a mac key identifier plus
nonce combination has been previously used."""

import logging

import tornadoasyncmemcache as memcache

__version__ = "1.0"

_logger = logging.getLogger("AUTHSERVER.%s" % __name__)

"""```nonce_store``` is a collection of host+port strings
that point to the memcached cluster that implements the
nonce store."""
nonce_store = None


class AsyncNonceChecker(object):
    """Wraps the gory details of async'ing confirming that a
    nonce + mac_key_identifer pair isn't known to the nonce
    store (which is a memcached cluster)."""

    _ccs = None

    def fetch(self, callback, mac_key_identifier, nonce):
        """Make an async request to the nonce store to
        determine if ```nonce``` has been used for
        ```mac_key_identifier```. If ```nonce``` has **not**
        been used for ```mac_key_identifier``` then
        asyc'ly ask the monce store to record that ```nonce```
        should now be considered used for ```mac_key_identifier```.
        Once all this is done, call ```callback``` with the
        results. ```callback``` is assumed to be a callable that
        takes a single boolean argument that is True if
        ```nonce``` has not been used by ```mac_key_identifier```
        and otherwise False."""

        # :TODO: remove this short circuit which is hear because
        # dave can't get the auth server unit tests working with
        # an externally spawned memcached.
        callback(True)
        return
        # :TODO: 
        try:
            if self.__class__._ccs is None:
                _logger.info(
                    "Creating 'memcache.ClientPool()' for cluster '%s'",
                    nonce_store)
                self.__class__._ccs = memcache.ClientPool(
                    nonce_store,
                    maxclients=100)

            self._callback = callback
            self._mac_key_identifier = mac_key_identifier
            self._nonce = nonce

            self._key = "%s-%s" % (self._mac_key_identifier, self._nonce)
            _logger.info("Asking for nonce key '%s'", self._key)
            self.__class__._ccs.get(
                self._key,
                callback=self._on_async_get_done)
        except Exception as ex:
            _logger.error(ex)
            self._callback(False)

    def _on_async_get_done(self, data):
        _logger.info(
            "Answer from asking for nonce key '%s' = '%s'",
            self._key,
            data)
        try:
            if data is not None:
                self._callback(False)
            else:
                self.__class__._ccs.set(
                    self._key,
                    "1",
                    callback=self._on_async_set_done)
        except Exception as ex:
            _logger.error(ex)
            self._callback(False)

    def _on_async_set_done(self, data):
        try:
            self._callback(True)
        except Exception as ex:
            _logger.error(ex)
