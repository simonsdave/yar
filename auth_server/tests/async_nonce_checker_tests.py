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

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_all_good(self):
        """..."""

        the_mac_key_identifier = mac.MACKeyIdentifier.generate()
        the_nonce = mac.Nonce.generate()

            
        def tornadoasyncmemcache_ClientPool_patch(nonce_store, maxclients):
            print "ctr() - %s - %s" % (nonce_store, maxclients)
            self.assertIsNotNone(nonce_store)
            self.assertEqual(nonce_store, self.__class__._nonce_store)

            def patched_get(key, callback):
                print "get() - %s - %s" % (key, callback)
                callback(None)

            def patched_set(key, value, callback):
                print "set() - %s - %s" % (key, value)
                callback(None)
                self.assertFalse(True)

            rv = mock.Mock()
            rv.get.side_effect = patched_get
            rv.set.side_effect = patched_set
            return rv

        with mock.patch("tornadoasyncmemcache.ClientPool", tornadoasyncmemcache_ClientPool_patch):
            def on_fetch_done(is_ok):
                print "on_fetch_done()"
                self.assertIsNotNone(is_ok)
                self.assertTrue(is_ok)

            aasf = async_nonce_checker.AsyncNonceChecker(
                the_mac_key_identifier,
                the_nonce)
            aasf.fetch(on_fetch_done)
