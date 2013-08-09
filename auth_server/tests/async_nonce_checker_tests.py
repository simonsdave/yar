"""This module implements the unit tests for the auth server's
vi async_nonce_checker  module."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mock

import mac
import yar_test_util

import async_nonce_checker

class TestAsyncNonceChecker(yar_test_util.TestCase):

    _nonce_store = ['localhost:11211']

    @classmethod
    def setUpClass(cls):
        async_nonce_checker.nonce_store = cls._nonce_store

    def _assertKey(self, mac_key_identifier, nonce, key):
        """Execute a number of asserts to gain confidence
        that ```key``` is the correct key to use when talking
        with memcached for ```mac_key_identifier``` and
        ```nonce```."""
        self.assertIsNotNone(mac_key_identifier)
        self.assertIsNotNone(nonce)
        expected_key = "%s-%s" % (mac_key_identifier, nonce)
        self.assertEqual(key, expected_key)

    def test_all_good(self):
        """..."""

        self._mac_key_identifier = mac.MACKeyIdentifier.generate()
        self._nonce = mac.Nonce.generate()
            
        self._mock = None

        def client_pool_class_patch(nonce_store, maxclients):
            self.assertIsNotNone(nonce_store)
            self.assertEqual(nonce_store, self.__class__._nonce_store)
            self.assertIsNotNone(maxclients)

            def patched_get(key, callback):
                self._assertKey(self._mac_key_identifier, self._nonce, key)
                # print "get()"
                callback(None)

            def patched_set(key, value, callback):
                self._assertKey(self._mac_key_identifier, self._nonce, key)
                # print "set()"
                self.assertIsNotNone(value)
                self.assertEqual(value, 1)
                callback(None)

            self.assertIsNone(self._mock)
            self._mock = mock.Mock()
            self._mock.get.side_effect = patched_get
            self._mock.set.side_effect = patched_set
            return self._mock

        name_of_class_to_patch = "tornadoasyncmemcache.ClientPool"
        with mock.patch(name_of_class_to_patch, client_pool_class_patch):
            def on_fetch_done(is_ok):
                self.assertIsNotNone(is_ok)
                self.assertTrue(is_ok)
                # print "done()"

            aasf = async_nonce_checker.AsyncNonceChecker(
                self._mac_key_identifier,
                self._nonce)
            aasf.fetch(on_fetch_done)
            # print ""
            # print '&'*50
            # print self._mock.mock_calls
            # print '^'*50
            # self.assertTrue(False)
