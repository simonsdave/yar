#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# auth_server_core_unit_tests.py
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

import testcase
import authenticationserver

#-------------------------------------------------------------------------------

class TestCase(testcase.TestCase):
	
	@classmethod
	def setUpClass(cls):
		cls.auth_server = testcase.AuthenticationServer()
		cls.auth_server.start()

		cls.key_server = testcase.KeyServer()
		cls.key_server.start()
		authenticationserver.RequestHandler.key_server = \
			"localhost:%d" % cls.key_server.port

	@classmethod
	def tearDownClass(cls):
		cls.auth_server.stop()
		cls.auth_server = None

		authenticationserver.RequestHandler.key_server = None
		cls.key_server.stop()
		cls.key_server = None

	def test_get_with_no_authorization_header(self):
		http_client = httplib2.Http()
		response, content = http_client.request(
			"http://localhost:%d/whatever" % self.__class__.auth_server.port,
			"GET")
		self.assertTrue(response.status == httplib.UNAUTHORIZED)

	def DAVE_test_get_with_invalid_authorization_header(self):
		http_client = httplib2.Http()
		response, content = http_client.request(
			self.url(),
			"GET",
			headers={"Authorization": 'MAC id="", nonce="98", mac="bindle"'})
		self.assertTrue(response.status == httplib.UNAUTHORIZED)

	def DAVE_test_get_with_unknonwn_mac_key_identifier(self):
		auth_header_value = 'MAC id="%s", nonce="98", mac="bindle"' % uuid.uuid4()
		http_client = httplib2.Http()
		response, content = http_client.request(
			self.url(),
			"GET",
			headers={"Authorization": auth_header_value})
		self.assertTrue(response.status == httplib.UNAUTHORIZED)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
