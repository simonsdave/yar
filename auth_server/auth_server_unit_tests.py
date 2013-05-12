#!/usr/bin/env python
"""This module contains the auth server's unit tests."""

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

		mac_key_identifier = mac.MACKeyIdentifier.generate()
		mac_key = mac.MACKey.generate()
		mac_algorithm = mac.MAC.algorithm
		owner = str(uuid.uuid4())
		http_method = "GET"
		uri = "/whatever"
		host = "localhost"
		port = self.__class__.auth_server.port
		content_type = None
		body = None

		ts = mac.Timestamp.generate()
		nonce = mac.Nonce.generate()
		ext = mac.Ext.generate(content_type, body)
		normalized_request_string = mac.NormalizedRequestString.generate(
			ts,
			nonce,
			http_method,
			uri,
			host,
			port,
			ext)
		my_mac = mac.MAC.generate(
			mac_key,
			mac_algorithm,
			normalized_request_string)
		auth_header_value = mac.AuthHeaderValue(
			mac_key_identifier,
			ts,
			nonce,
			ext,
			my_mac)

		http_client = httplib2.Http()
		response, content = http_client.request(
			"http://localhost:%d%s" % (self.__class__.auth_server.port, uri),
			"GET",
			headers={"Authorization": str(auth_header_value)})
		self.assertTrue(response.status == httplib.UNAUTHORIZED)
		self.assertMACKeyIdentifierInKeyServerRequest(mac_key_identifier)

	def test_invalid_mac_algorithm_returned_from_key_server(self):
		mac_key_identifier = mac.MACKeyIdentifier.generate()
		mac_key = mac.MACKey.generate()
		mac_algorithm = mac.MAC.algorithm
		owner = str(uuid.uuid4())
		http_method = "GET"
		uri = "/whatever"
		host = "localhost"
		port = self.__class__.auth_server.port
		content_type = None
		body = None

		testcase.TestCase.mac_key_in_response_to_key_server_request = mac_key
		testcase.TestCase.mac_algorithm_response_to_key_server_request = "dave-%s" % mac_algorithm
		testcase.TestCase.owner_in_response_to_key_server_request = owner

		ts = mac.Timestamp.generate()
		nonce = mac.Nonce.generate()
		ext = mac.Ext.generate(content_type, body)
		normalized_request_string = mac.NormalizedRequestString.generate(
			ts,
			nonce,
			http_method,
			uri,
			host,
			port,
			ext)
		my_mac = mac.MAC.generate(
			mac_key,
			mac_algorithm,
			normalized_request_string)
		auth_header_value = mac.AuthHeaderValue(
			mac_key_identifier,
			ts,
			nonce,
			ext,
			my_mac)
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
			owner,
			mac_key_identifier)

	def test_all_good_on_get(self):
		mac_key_identifier = mac.MACKeyIdentifier.generate()
		mac_key = mac.MACKey.generate()
		mac_algorithm = mac.MAC.algorithm
		owner = str(uuid.uuid4())
		http_method = "GET"
		uri = "/whatever"
		host = "localhost"
		port = self.__class__.auth_server.port
		content_type = None
		body = None

		testcase.TestCase.mac_key_in_response_to_key_server_request = mac_key
		testcase.TestCase.mac_algorithm_response_to_key_server_request = mac_algorithm
		testcase.TestCase.owner_in_response_to_key_server_request = owner

		ts = mac.Timestamp.generate()
		nonce = mac.Nonce.generate()
		ext = mac.Ext.generate(content_type, body)
		normalized_request_string = mac.NormalizedRequestString.generate(
			ts,
			nonce,
			http_method,
			uri,
			host,
			port,
			ext)
		my_mac = mac.MAC.generate(
			mac_key,
			mac_algorithm,
			normalized_request_string)
		auth_header_value = mac.AuthHeaderValue(
			mac_key_identifier,
			ts,
			nonce,
			ext,
			my_mac)
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
			owner,
			mac_key_identifier)

	def test_all_good_on_post(self):
		mac_key_identifier = mac.MACKeyIdentifier.generate()
		mac_key = mac.MACKey.generate()
		mac_algorithm = mac.MAC.algorithm
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

		ts = mac.Timestamp.generate()
		nonce = mac.Nonce.generate()
		ext = mac.Ext.generate(content_type, body)
		normalized_request_string = mac.NormalizedRequestString.generate(
			ts,
			nonce,
			http_method,
			uri,
			host,
			port,
			ext)
		my_mac = mac.MAC.generate(
			mac_key,
			mac_algorithm,
			normalized_request_string)
		auth_header_value = mac.AuthHeaderValue(
			mac_key_identifier,
			ts,
			nonce,
			ext,
			my_mac)
		auth_header_value = str(auth_header_value)
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
			owner,
			mac_key_identifier)

	def _send_get_to_auth_server(
		self,
		mac_key_identifier,
		mac_key,
		mac_algorithm,
		owner,
		seconds_to_subtract_from_ts=None):
		"""Utility method for issuing HTTP GETs to the auth server
		with the provided credentials."""

		http_method = "GET"
		uri = "/whatever"
		host = "localhost"
		port = self.__class__.auth_server.port
		content_type = None
		body = None

		ts = mac.Timestamp.generate()
		if seconds_to_subtract_from_ts is not None:
			ts = mac.Timestamp(int(ts) - seconds_to_subtract_from_ts)
		nonce = mac.Nonce.generate()
		ext = mac.Ext.generate(content_type, body)
		normalized_request_string = mac.NormalizedRequestString.generate(
			ts,
			nonce,
			http_method,
			uri,
			host,
			port,
			ext)
		my_mac = mac.MAC.generate(
			mac_key,
			mac_algorithm,
			normalized_request_string)
		auth_header_value = mac.AuthHeaderValue(
			mac_key_identifier,
			ts,
			nonce,
			ext,
			my_mac)

		http_client = httplib2.Http()
		response, content = http_client.request(
			"http://localhost:%d%s" % (self.__class__.auth_server.port, uri),
			"GET",
			headers={"Authorization": str(auth_header_value)})
		return (response, content)

	def test_get_with_old_timestamp(self):
		# establish credentials
		mac_key_identifier = mac.MACKeyIdentifier.generate()
		mac_key = mac.MACKey.generate()
		mac_algorithm = mac.MAC.algorithm
		owner = str(uuid.uuid4())

		# configure mock key server with established credentials
		testcase.TestCase.mac_key_in_response_to_key_server_request = mac_key
		testcase.TestCase.mac_algorithm_response_to_key_server_request = mac_algorithm
		testcase.TestCase.owner_in_response_to_key_server_request = owner

		# initially confirm all good with a simple GET request
		response, content = self._send_get_to_auth_server(
			mac_key_identifier,
			mac_key,
			mac_algorithm,
			owner)
		self.assertTrue(response.status == httplib.OK)

		# now repeat the all good GET but this time ask for the request's
		# timestamp to be reduced by # of seconds in one year
		one_year_in_seconds = 365*24*60
		response, content = self._send_get_to_auth_server(
			mac_key_identifier,
			mac_key,
			mac_algorithm,
			owner,
			seconds_to_subtract_from_ts=one_year_in_seconds)
		self.assertTrue(response.status == httplib.UNAUTHORIZED)

		# now repeat the all good GET but this time ask for the request's
		# timestamp to be advanced by one day
		one_day_in_seconds = 24*60
		response, content = self._send_get_to_auth_server(
			mac_key_identifier,
			mac_key,
			mac_algorithm,
			owner,
			seconds_to_subtract_from_ts=-one_day_in_seconds)
		self.assertTrue(response.status == httplib.UNAUTHORIZED)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
