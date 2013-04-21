#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# key_server_unit_tests.py
#
#-------------------------------------------------------------------------------

import logging
logging.basicConfig( level=logging.FATAL )
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

import key_server

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

		http_server = tornado.httpserver.HTTPServer(key_server._tornado_app)
		http_server.add_sockets([sock])

		# this might not be required but want to give the server 
		# a bit of time to get itself settled
		time.sleep(1)

	def run(self):
		tornado.ioloop.IOLoop.instance().start()

	def stop(self):
		tornado.ioloop.IOLoop.instance().stop()

#-------------------------------------------------------------------------------

class KeyServerTestCase(unittest.TestCase):
	
	_json_utf8_content_type_reg_ex = re.compile(
		"^\s*application/json;\s+charset\=utf-{0,1}8\s*$",
		re.IGNORECASE )

	@classmethod
	def setUpClass(cls):
		cls._key_server = KeyServer()
		cls._key_server.start()

	@classmethod
	def tearDownClass(cls):
		cls._key_server.stop()
		cls._key_server = None

	def url(self):
		return "http://localhost:%s" % self.__class__._key_server.port

	"""
	method name/style chosen for consistency with unittest.TestCase
	"""
	def assertIsJsonUtf8ContentType(self,content_type):
		self.assertIsNotNone(content_type)
		json_utf8_content_type_reg_ex = self.__class__._json_utf8_content_type_reg_ex
		self.assertIsNotNone(json_utf8_content_type_reg_ex.match(content_type))

#-------------------------------------------------------------------------------

class TestStatusResource(KeyServerTestCase):
	
	def url(self):
		return "%s/status" % KeyServerTestCase.url(self)

	def test_get(self):
		http_client = httplib2.Http()
		response, content = http_client.request(self.url(), "GET")

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
		response, content = http_client.request(self.url(), method)
		self.assertIsNotNone(response)
		self.assertTrue(httplib.METHOD_NOT_ALLOWED == response.status)

	def test_post(self):
		self._test_bad_method("POST")

	def test_put(self):
		self._test_bad_method("PUT")

	def test_delete(self):
		self._test_bad_method("DELETE")

#-------------------------------------------------------------------------------

class TestMacCredsResource(KeyServerTestCase):

	def url(self):
		return "%s/v1.0/mac_creds" % KeyServerTestCase.url(self)

	def _create_creds(self, owner):
		self.assertIsNotNone(owner)
		self.assertTrue(0 < len(owner))

		# create the resource
		http_client = httplib2.Http()
		response, content = http_client.request(
			self.url(),
			"POST",
			body=json.dumps({"owner": owner}),
			headers={"Content-Type": "application/json; charset=utf8"}
			)
		self.assertIsNotNone(response)
		self.assertTrue(httplib.CREATED == response.status)
		self.assertTrue('location' in response)
		location = response['location']
		self.assertIsNotNone(location)
		self.assertIsNotNone(location.startswith(self.url()))

		# based on the returned location retrieve the newly created MAC creds
		http_client = httplib2.Http()
		response, content = http_client.request(location, "GET")
		self.assertTrue(httplib.OK == response.status)
		self.assertTrue("content-type" in response)
		content_type = response["content-type"]
		self.assertIsJsonUtf8ContentType(content_type)
		creds = json.loads(content)
		self.assertIsNotNone(creds)
		self.assertEqual(owner, creds.get('owner', None))
		mac_key_identifier = creds.get('mac_key_identifier', None)
		self.assertIsNotNone(mac_key_identifier)
		self.assertTrue(location.endswith(mac_key_identifier))

		return (creds, location)

	def _get_all_creds(self, owner=None):
		http_client = httplib2.Http()
		url = self.url()
		if owner is not None:
			self.assertTrue(0 < len(owner))
			url = "%s?owner=%s" % (url, owner)
		response, content = http_client.request(url, "GET")
		self.assertIsNotNone(response)
		print url
		print response
		print content
		self.assertTrue(httplib.OK == response.status)
		self.assertTrue("content-type" in  response)
		content_type = response["content-type"]
		self.assertIsJsonUtf8ContentType(content_type)
		self.assertTrue("content-length" in  response)
		content_length = response["content-length"]
		content_length = int(content_length)
		self.assertTrue(0 < content_length)
		self.assertIsNotNone(content)
		self.assertTrue(0 < len(content))
		self.assertEqual(content_length, len(content))
		creds = json.loads(content)
		self.assertIsNotNone(creds)
		return creds

	def _delete_creds(self, mac_key_identifier):
		self.assertIsNotNone(mac_key_identifier)
		self.assertTrue(0<len(mac_key_identifier))

		url = "%s/%s" % (self.url(), mac_key_identifier)
		http_client = httplib2.Http()
		response, content = http_client.request(url, "DELETE")
		self.assertTrue(httplib.OK == response.status)

	def _delete_all_creds(self, owner=None):
		all_creds = self._get_all_creds(owner)
		self.assertIsNotNone(all_creds)
		for creds in all_creds:
			self.assertTrue("mac_key_identifier" in creds)
			mac_key_identifier = creds["mac_key_identifier"]
			self._delete_creds(mac_key_identifier)
		all_creds = self._get_all_creds(owner)
		self.assertIsNotNone(all_creds)
		self.assertEqual(0, len(all_creds))

	def test_get_of_non_existent_resource(self):
		url = "%s/%s" % (self.url(), str(uuid.uuid4()).replace("-",""))
		http_client = httplib2.Http()
		response, content = http_client.request(url, "GET")
		self.assertIsNotNone(response)
		self.assertTrue(httplib.NOT_FOUND == response.status)

	def test_post_with_no_content_type_header(self):
		http_client = httplib2.Http()
		response, content = http_client.request(
			self.url(),
			"POST",
			body=json.dumps({"owner": "simonsdave@gmail.com"}),
			headers={}
			)
		self.assertIsNotNone(response)
		self.assertTrue(httplib.BAD_REQUEST == response.status)

	def test_post_with_unsupported_content_type_header(self):
		http_client = httplib2.Http()
		response, content = http_client.request(
			self.url(),
			"POST",
			body=json.dumps({"owner": "simonsdave@gmail.com"}),
			headers={"Content-Type": "text/plain"}
			)
		self.assertIsNotNone(response)
		self.assertTrue(httplib.BAD_REQUEST == response.status)

	def test_post_with_no_body(self):
		http_client = httplib2.Http()
		response, content = http_client.request(
			self.url(),
			"POST",
			headers={"Content-Type": "application/json; charset=utf8"}
			)
		self.assertIsNotNone(response)
		self.assertTrue(httplib.BAD_REQUEST == response.status)

	def test_post_with_zero_length_body(self):
		http_client = httplib2.Http()
		response, content = http_client.request(
			self.url(),
			"POST",
			body="",
			headers={"Content-Type": "application/json; charset=utf8"}
			)
		self.assertIsNotNone(response)
		self.assertTrue(httplib.BAD_REQUEST == response.status)

	def test_post_with_non_json_body(self):
		http_client = httplib2.Http()
		response, content = http_client.request(
			self.url(),
			"POST",
			body="dave_was_here",
			headers={"Content-Type": "application/json; charset=utf8"}
			)
		self.assertIsNotNone(response)
		self.assertTrue(httplib.BAD_REQUEST == response.status)

	def test_post_with_no_owner_in_body(self):
		http_client = httplib2.Http()
		response, content = http_client.request(
			self.url(),
			"POST",
			body=json.dumps({"XXXownerXXX": "simonsdave@gmail.com"}),
			headers={"Content-Type": "application/json; charset=utf8"}
			)
		self.assertIsNotNone(response)
		self.assertTrue(httplib.BAD_REQUEST == response.status)

	def test_delete_method_on_creds_collection_resource(self):
		http_client = httplib2.Http()
		response, content = http_client.request(self.url(), "DELETE")
		self.assertIsNotNone(response)
		self.assertTrue(httplib.METHOD_NOT_ALLOWED == response.status)

	def test_put_method_on_creds_collection_resource(self):
		http_client = httplib2.Http()
		response, content = http_client.request(self.url(), "DELETE")
		self.assertIsNotNone(response)
		self.assertTrue(httplib.METHOD_NOT_ALLOWED == response.status)

	def test_post_method_on_creds_resource(self):
		http_client = httplib2.Http()
		url = "%s/%s" % (self.url(), "dave")
		response, content = http_client.request(url, "POST")
		self.assertIsNotNone(response)
		self.assertTrue(httplib.METHOD_NOT_ALLOWED == response.status)

	def test_put_method_on_creds_resource(self):
		http_client = httplib2.Http()
		url = "%s/%s" % (self.url(), "dave")
		response, content = http_client.request(url, "PUT")
		self.assertIsNotNone(response)
		self.assertTrue(httplib.METHOD_NOT_ALLOWED == response.status)

	def test_get_by_owner(self):
		self._delete_all_creds()

		owner = str(uuid.uuid4()).replace("-","")
		owner_creds = []
		for x in range(1,11):
			owner_creds.append(self._create_creds(owner))

		other_owner = str(uuid.uuid4()).replace("-","")
		other_owner_creds = []
		for x in range(1,4):
			other_owner_creds.append(self._create_creds(other_owner))

		all_owner_creds = self._get_all_creds(owner)
		self.assertIsNotNone(all_owner_creds)
		self.assertEqual(len(all_owner_creds), len(owner_creds))

		for creds in (owner_creds + other_owner_creds):
			self._delete_creds(creds[0]['mac_key_identifier'])

	def test_all_good_for_simple_create_and_delete(self):
		self._delete_all_creds()

		all_creds = self._get_all_creds()
		self.assertIsNotNone(all_creds)
		self.assertEqual(0, len(all_creds))

		owner = str(uuid.uuid4()).replace("-","")
		(creds, location) = self._create_creds(owner)
		self.assertIsNotNone(creds)
		mac_key_identifier = creds.get('mac_key_identifier', None)
		self.assertIsNotNone(mac_key_identifier)
		self.assertTrue(0 < len(mac_key_identifier))

		self._delete_creds(mac_key_identifier)
		self._delete_creds(mac_key_identifier)

		all_creds = self._get_all_creds()
		self.assertIsNotNone(all_creds)
		self.assertEqual(0, len(all_creds))

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
