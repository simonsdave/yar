import socket
import subprocess
import time
import unittest

import memcache

class NonceStore(object):

    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 0))
        port = sock.getsockname()[1]

        args = [
            "memcached",
            "-vv",
            "-p",
            str(port),
            "-U",
            str(port),
            "-l",
            "localhost"
        ]
        self.process = subprocess.Popen(args, shell=False)

        mc = memcache.Client(["localhost:%d" % port], debug=1)
        key = "some_key"
        value = None
        for attempt in range(0, 100):
            print mc.get_stats()
            print mc.set(key, "Some value")
            value = mc.get(key)
            print "%d >>>%s<<<" % (attempt, value)
            if value is not None:
                break
            time.sleep(1)

    def shutdown(self):
        self.process.terminate()
        
class TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.nonce_store = NonceStore()

    @classmethod
    def tearDownClass(cls):
        cls.nonce_store.shutdown()
        cls.nonce_store = None

    def test_dave(self):
        self.assertTrue(True)

