#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# auth_server_auth_unit_tests.py
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

import testcase
import auth_server

#-------------------------------------------------------------------------------

class TestCase(testcase.TestCase):
	
	@classmethod
	def setUpClass(cls):
		cls.auth_server = testcase.AuthenticationServer()

		cls.key_server = testcase.KeyServer()
		auth_server.AuthRequestHandler.key_server = \
			"localhost:%d" % cls.key_server.port

		cls.app_server = testcase.AppServer()
		auth_server.AuthRequestHandler.app_server = \
			"localhost:%d" % cls.app_server.port

		cls.io_loop = testcase.IOLoop()
		cls.io_loop.start()

	@classmethod
	def tearDownClass(cls):
		cls.auth_server = None
		cls.key_server = None
		cls.io_loop.stop()
		cls.io_loop = None

	def test_get_with_no_authorization_header(self):
		http_client = httplib2.Http()
		response, content = http_client.request(
			"http://localhost:%d/whatever" % self.__class__.auth_server.port,
			"GET")
		self.assertTrue(response.status == httplib.UNAUTHORIZED)

	def test_get_with_invalid_authorization_header(self):
		http_client = httplib2.Http()
		response, content = http_client.request(
			"http://localhost:%d/whatever" % self.__class__.auth_server.port,
			"GET",
			headers={"Authorization": 'MAC id="", nonce="98", mac="bindle"'})
		self.assertTrue(response.status == httplib.UNAUTHORIZED)

	def test_get_with_unknonwn_mac_key_identifier(self):
		auth_header_value = 'MAC id="%s", nonce="98", mac="bindle"' % uuid.uuid4()
		http_client = httplib2.Http()
		response, content = http_client.request(
			"http://localhost:%d/whatever" % self.__class__.auth_server.port,
			"GET",
			headers={"Authorization": auth_header_value})
		self.assertTrue(response.status == httplib.UNAUTHORIZED)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
