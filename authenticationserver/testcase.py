#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# testcase.py
#
#-------------------------------------------------------------------------------

import logging
logging.basicConfig(level=logging.ERROR)
import time
import socket
import threading
import unittest
import re
import httplib
import httplib2
import json
import uuid

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.netutil

import auth_server

#-------------------------------------------------------------------------------

class KeyServerRequestHandler(tornado.web.RequestHandler):

    def get(self):
		uri_reg_ex = re.compile(
			'^/v1\.0/mac_creds/(?P<mac_key_identifier>.+)$',
			re.IGNORECASE )
		match = uri_reg_ex.match(self.request.uri)
		if not match:
			self.set_status(httplib.NOT_FOUND)
		else:
			assert 0 == match.start()
			assert len(self.request.uri) == match.end()
			assert 1 == len(match.groups())
			mac_key_identifier = match.group("mac_key_identifier")
			assert mac_key_identifier is not None
			assert 0 < len(mac_key_identifier)

			dict = {
				"mac_key_identifier": mac_key_identifier,
				"mac_key": "def",
				"mac_algorithm": "def",
				"issue_time": "def",
				}
			body = json.dumps(dict)
			self.write(body)
			self.set_header("Content-Type", "application/json; charset=utf8")
			self.set_status(httplib.OK)

#-------------------------------------------------------------------------------

class KeyServer(threading.Thread):

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

		handlers=[(r".*", KeyServerRequestHandler)]
		app = tornado.web.Application(handlers=handlers)
		http_server = tornado.httpserver.HTTPServer(app)
		http_server.add_sockets([sock])

		# this might not be required but want to give the server 
		# a bit of time to get itself settled
		time.sleep(1)

	def run(self):
		tornado.ioloop.IOLoop.instance().start()

	def stop(self):
		tornado.ioloop.IOLoop.instance().stop()

#-------------------------------------------------------------------------------

class AuthenticationServer(threading.Thread):

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

		http_server = tornado.httpserver.HTTPServer(auth_server._tornado_app)
		http_server.add_sockets([sock])

		# this might not be required but want to give the server 
		# a bit of time to get itself settled
		time.sleep(1)

	def run(self):
		tornado.ioloop.IOLoop.instance().start()

	def stop(self):
		tornado.ioloop.IOLoop.instance().stop()

#-------------------------------------------------------------------------------

class TestCase(unittest.TestCase):
	
	def assertIsJsonUtf8ContentType(self,content_type):
		"""A method name/style chosen for consistency with unittest.TestCase
		which allows the caller to assert if the 'content_type' argument
		is a valid value for the Content-type HTTP header. """
		self.assertIsNotNone(content_type)
		json_utf8_content_type_reg_ex = re.compile(
			"^\s*application/json;\s+charset\=utf-{0,1}8\s*$",
			re.IGNORECASE )
		self.assertIsNotNone(json_utf8_content_type_reg_ex.match(content_type))

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	pass

#------------------------------------------------------------------- End-of-File
