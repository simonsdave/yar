#!/usr/bin/env python
"""This module implements the key server's unit tests."""

import logging
logging.basicConfig(level=logging.FATAL)
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

import testutil
import key_server
import key_store.key_store_installer

#-------------------------------------------------------------------------------

class KeyServer(threading.Thread):

	def __init__(self, key_store):
		threading.Thread.__init__(self)
		self.daemon = True

		key_server._key_store = key_store

		(self.socket, self.port) = testutil.get_available_port()

		http_server = tornado.httpserver.HTTPServer(key_server._tornado_app)
		http_server.add_sockets([self.socket])

		# this might not be required but want to give the server 
		# a bit of time to get itself settled
		time.sleep(1)

	def run(self):
		tornado.ioloop.IOLoop.instance().start()

	def stop(self):
		tornado.ioloop.IOLoop.instance().stop()

#-------------------------------------------------------------------------------

class KeyServerTestCase(testutil.TestCase):
	
	_database_name = None

	@classmethod
	def setUpClass(cls):
		cls._database_name = "das%s" % str(uuid.uuid4()).replace("-","")[:7]
		key_store.key_store_installer.create(cls._database_name)
		cls._key_server = KeyServer("localhost:5984/%s" % cls._database_name)
		cls._key_server.start()

	@classmethod
	def tearDownClass(cls):
		cls._key_server.stop()
		cls._key_server = None
		key_store.key_store_installer.delete(cls._database_name)
		cls._database_name = None

	def url(self):
		return "http://localhost:%s" % self.__class__._key_server.port

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
		return "%s/v1.0/creds" % KeyServerTestCase.url(self)

	def _get_creds(self, mac_key_identifier, expected_to_be_found=True, get_deleted=False):
		self.assertIsNotNone(mac_key_identifier)
		self.assertTrue(0 < len(mac_key_identifier))
		url = "%s/%s" % (self.url(), mac_key_identifier)
		if get_deleted:
			url = "%s?deleted=true" % url
		http_client = httplib2.Http()
		response, content = http_client.request(url, "GET")
		if not expected_to_be_found:
			self.assertTrue(httplib.NOT_FOUND == response.status)
			return None
		self.assertTrue(httplib.OK == response.status)
		self.assertTrue("content-type" in response)
		content_type = response["content-type"]
		self.assertIsJsonUtf8ContentType(content_type)
		creds = json.loads(content)
		self.assertIsNotNone(creds)
		self.assertTrue("mac_key_identifier" in creds)
		self.assertEqual(mac_key_identifier, creds["mac_key_identifier"])
		return creds

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
		self.assertTrue('content-location' in response)
		content_location = response['content-location']
		self.assertIsNotNone(content_location)
		self.assertIsNotNone(content_location.startswith(self.url()))

		# based on the returned content_location retrieve the newly created MAC creds
		http_client = httplib2.Http()
		response, content = http_client.request(content_location, "GET")
		self.assertTrue(httplib.OK == response.status)
		self.assertTrue("content-type" in response)
		content_type = response["content-type"]
		self.assertIsJsonUtf8ContentType(content_type)
		creds = json.loads(content)
		self.assertIsNotNone(creds)
		self.assertEqual(owner, creds.get('owner', None))
		mac_key_identifier = creds.get('mac_key_identifier', None)
		self.assertIsNotNone(mac_key_identifier)
		self.assertTrue(content_location.endswith(mac_key_identifier))

		# this is really over the top but that's the way I roll:-)
		self._get_creds(mac_key_identifier)

		return (creds, content_location)

	def _get_all_creds(self, owner=None):
		http_client = httplib2.Http()
		url = self.url()
		if owner is not None:
			self.assertTrue(0 < len(owner))
			url = "%s?owner=%s" % (url, owner)
		response, content = http_client.request(url, "GET")
		self.assertIsNotNone(response)
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

	def test_deleted_creds_not_returned_by_default_on_get(self):
		owner = str(uuid.uuid4()).replace("-","")
		(creds_on_create, location_on_create) = self._create_creds(owner)
		mac_key_identifier = creds_on_create["mac_key_identifier"]
		creds_on_get_before_delete = self._get_creds(mac_key_identifier)
		self.assertIsNotNone(creds_on_get_before_delete)
		self._delete_creds(mac_key_identifier)
		self._get_creds(mac_key_identifier, expected_to_be_found=False)
		self._get_creds(mac_key_identifier, get_deleted=True)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
