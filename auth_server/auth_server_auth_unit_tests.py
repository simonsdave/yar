#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# auth_server_auth_unit_tests.py
#
#-------------------------------------------------------------------------------

import logging
logging.basicConfig(level=logging.INFO)
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
		cls.app_server = testcase.AppServer()
		cls.app_server_auth_method = str(uuid.uuid4()).replace("-","")
		cls.key_server = testcase.KeyServer()
		cls.auth_server = testcase.AuthenticationServer(
			cls.key_server,
			cls.app_server,
			cls.app_server_auth_method)

		cls.io_loop = testcase.IOLoop()
		cls.io_loop.start()

	@classmethod
	def tearDownClass(cls):
		cls.app_server = None
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

	def test_all_good_on_get(self):
		mac_key_identifier = str(uuid.uuid4())
		mac_key = str(uuid.uuid4())
		mac_algorithm = "hmac-sha-1"
		owner = str(uuid.uuid4())
		http_method = "GET"
		uri = "/whatever"
		host = "localhost"
		port = self.__class__.auth_server.port

		testcase.TestCase.mac_key_in_response_to_key_server_request = mac_key
		testcase.TestCase.mac_algorithm_response_to_key_server_request = mac_algorithm
		testcase.TestCase.owner_in_response_to_key_server_request = owner

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
		self.assertAppServerRequest(get=True)
		self.assertMACKeyIdentifierInKeyServerRequest(mac_key_identifier)
		self.assertAuthorizationHeaderInAppServerRequest(
			self.__class__.app_server_auth_method,
			owner)

	def test_all_good_on_post(self):
		mac_key_identifier = str(uuid.uuid4())
		mac_key = str(uuid.uuid4())
		mac_algorithm = "hmac-sha-1"
		owner = str(uuid.uuid4())
		http_method = "POST"
		uri = "/isallokonpost"
		host = "localhost"
		port = self.__class__.auth_server.port
		content_type = "application/json; charset=utf-8"
		body = json.dumps({"dave": "was", "here": "today"})

		testcase.TestCase.mac_key_in_response_to_key_server_request = mac_key
		testcase.TestCase.mac_algorithm_response_to_key_server_request = mac_algorithm
		testcase.TestCase.owner_in_response_to_key_server_request = owner

		auth_header_value = mac.AuthHeader(
			mac_key_identifier,
			mac_key,
			mac_algorithm,
			http_method,
			uri,
			host,
			port,
			content_type,
			body)
		http_client = httplib2.Http()
		headers = {
			"Authorization": str(auth_header_value),
			"Content-Type": content_type,
			}
		response, content = http_client.request(
			"http://%s:%d%s" % (host, port, uri),
			http_method,
			headers=headers,
			body=body)
		self.assertTrue(response.status == httplib.OK)
		self.assertAppServerRequest(post=True)
		self.assertMACKeyIdentifierInKeyServerRequest(mac_key_identifier)
		self.assertAuthorizationHeaderInAppServerRequest(
			self.__class__.app_server_auth_method,
			owner)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
