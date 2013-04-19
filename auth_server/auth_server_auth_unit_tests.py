#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# auth_server_auth_unit_tests.py
#
#-------------------------------------------------------------------------------

import logging
logging.basicConfig(level=logging.FATAL)
import unittest
import httplib
import httplib2
import json
import uuid

import testcase
import auth_server
import mac

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
		cls.app_server = None
		cls.io_loop.stop()
		cls.io_loop = None

	def test_key_server_responding_with_invalid_mac_algorithm(self):
		mac_key_identifier = str(uuid.uuid4())
		mac_key = str(uuid.uuid4())
		mac_algorithm = "hmac-sha-1"
		http_method = "GET"
		uri = "/whatever"
		host = "localhost"
		port = self.__class__.auth_server.port

		testcase.TestCase.mac_key_in_response_to_key_server_request = mac_key
		testcase.TestCase.mac_algorithm_response_to_key_server_request = mac_algorithm

		auth_header_value = mac.AuthHeader(
			mac_key_identifier,
			mac_key,
			mac_algorithm,
			http_method,
			uri,
			host,
			port)
		auth_header_value = str(auth_header_value)
		http_client = httplib2.Http()
		response, content = http_client.request(
			"http://%s:%d%s" % (host, port, uri),
			http_method,
			headers={"Authorization": auth_header_value})
		self.assertTrue(response.status == httplib.OK)
		self.assertMACKeyIdentifierInKeyServerRequest(mac_key_identifier)

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
			headers={"Authorization": 'MAC id="", ts="890", nonce="98", ext="abc", mac="bindle"'})
		self.assertTrue(response.status == httplib.UNAUTHORIZED)

	def test_get_with_unknonwn_mac_key_identifier(self):
		testcase.TestCase.status_code_of_response_to_key_server_request = httplib.NOT_FOUND
		mac_key_identifier = str(uuid.uuid4())
		auth_header_value = 'MAC id="%s", ts="890", nonce="98", ext="def", mac="bindle"' % mac_key_identifier
		http_client = httplib2.Http()
		response, content = http_client.request(
			"http://localhost:%d/whatever" % self.__class__.auth_server.port,
			"GET",
			headers={"Authorization": auth_header_value})
		self.assertTrue(response.status == httplib.UNAUTHORIZED)
		self.assertMACKeyIdentifierInKeyServerRequest(mac_key_identifier)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
