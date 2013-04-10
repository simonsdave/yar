#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# auth_server_status_unit_tests.py
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

#-------------------------------------------------------------------------------

class TestStatusResource(testcase.TestCase):
	
	@classmethod
	def setUpClass(cls):
		cls.auth_server = testcase.AuthenticationServer()
		cls.auth_server.start()

	@classmethod
	def tearDownClass(cls):
		cls.auth_server.stop()
		cls.auth_server = None

	def test_get(self):
		http_client = httplib2.Http()
		response, content = http_client.request(
			"http://localhost:%d/status" % self.__class__.auth_server.port,
			"GET")
		self.assertIsNotNone(response)

		self.assertTrue(httplib.OK == response.status)
		self.assertTrue("content-type" in response)
		content_type = response["content-type"]
		self.assertIsJsonUtf8ContentType(content_type)

		self.assertIsNotNone(content)
		content = json.loads(content)
		self.assertTrue("status" in content)
		self.assertTrue(content["status"] == "ok")
		self.assertTrue("version" in content)
		self.assertTrue(content["version"] == "1.0")

	def _test_bad_method(self,method):
		http_client = httplib2.Http()
		response, content = http_client.request(
			"http://localhost:%d/status" % self.__class__.auth_server.port,
			method)
		self.assertIsNotNone(response)
		self.assertTrue(httplib.METHOD_NOT_ALLOWED == response.status)

	def test_post(self):
		self._test_bad_method("POST")

	def test_put(self):
		self._test_bad_method("PUT")

	def test_delete(self):
		self._test_bad_method("DELETE")

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
