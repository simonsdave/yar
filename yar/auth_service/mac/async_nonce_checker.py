"""This module hides the gory details of async'ly interacting
with the nonce store to determine if a mac key identifier plus
nonce combination has been previously used."""

import datetime
import logging

import tornadoasyncmemcache

_logger = logging.getLogger("AUTHSERVICE.%s" % __name__)

"""```nonce_store``` is a collection of host:port strings
that point to the memcached cluster that implements the
nonce store."""
nonce_store = ["127.0.0.1:11211"]


class AsyncNonceChecker(object):
    """Wraps the gory details of async'ing confirming that a
    nonce + mac_key_identifer pair isn't known to the nonce
    store (which is a memcached cluster)."""

    _ccs = None

    def __init__(self, mac_key_identifier, nonce):
        object.__init__(self)

        self._mac_key_identifier = mac_key_identifier
        self._nonce = nonce

    def fetch(self, callback):
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
        self._callback = callback

        self._key = "%s-%s" % (self._mac_key_identifier, self._nonce)

        _logger.info("Asking for nonce key '%s'", self._key)

        self._start_timestamp = datetime.datetime.now()

        type(self).ccs().get(
            self._key,
            callback=self._on_async_get_done)

    def _on_async_get_done(self, data):

        self._log_duration("get")

        _logger.info(
            "Answer from asking for nonce key '%s' = '%s'",
            self._key,
            data)

        if data is not None:
            self._callback(False)
        else:
            self._start_timestamp = datetime.datetime.now()
            type(self).ccs().set(
                self._key,
                1,
                callback=self._on_async_set_done)

    def _on_async_set_done(self, data):

        self._log_duration("set")

        self._callback(True)

    def _log_duration(self, operation):
        stop_timestamp = datetime.datetime.now()
        duration = stop_timestamp - self._start_timestamp
        _logger.info(
            "Nonce Store (%s - %s) responded in %d us",
            operation,
            self._key,
            duration.microseconds)

    @classmethod
    def ccs(cls):
        if cls._ccs is None:
            _logger.info(
                "Creating 'tornadoasyncmemcache.ClientPool()' for cluster '%s'",
                nonce_store)
            cls._ccs = tornadoasyncmemcache.ClientPool(
                nonce_store,
                maxclients=100)
        return cls._ccs
