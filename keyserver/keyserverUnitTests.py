#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# keyserverUnitTests.py
#
#-------------------------------------------------------------------------------

import time
import socket
import threading
import unittest

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.netutil

import keyserver

#-------------------------------------------------------------------------------

class HTTPServer(threading.Thread):

	@classmethod
	def _get_socket(cls):
		[sock] = tornado.netutil.bind_sockets(
			0,
			"localhost",
			family=socket.AF_INET)
		return sock

	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True

		sock = self.__class__._get_socket()
		self.port = sock.getsockname()[1]

		http_server = tornado.httpserver.HTTPServer(keyserver._tornado_app)
		http_server.add_sockets([sock])

	def run(self):
		tornado.ioloop.IOLoop.instance().start()

	def stop(self):
		tornado.ioloop.IOLoop.instance().stop()

#------------------------------------------------------------------- End-of-File

class Test(unittest.TestCase):
	
	@classmethod
	def setUpClass(cls):
		cls._http_server = HTTPServer()
		cls._http_server.start()

	@classmethod
	def tearDownClass(cls):
		cls._http_server.stop()
		cls._http_server = None

	def test_ctr( self ):
		# self.assertTrue( mac_credentials.owner == owner )
		time.sleep(2)
		print self.__class__._http_server.port

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
