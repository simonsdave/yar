import socket
import subprocess
import sys
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
#           "-vv",
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
            sys.stderr.write("%d >>>%s<<<\n" % (attempt, value))
            if value is not None:
                break
            time.sleep(1)

    def shutdown(self):
        sys.stderr.write("Shutting down memcached\n")
        self.process.terminate()
        self.process = None
        

class TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.nonce_store = NonceStore()
        sys.stderr.write("Nonce Store running\n")

    @classmethod
    def tearDownClass(cls):
        cls.nonce_store.shutdown()
        cls.nonce_store = None
        sys.stderr.write("Nonce Store shutdown\n")

    def test_dave(self):
        pass

    def test_hello(self):
        pass
