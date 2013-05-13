#-------------------------------------------------------------------------------
#
# testcase.py
#
#-------------------------------------------------------------------------------

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

import auth_server

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

class Server(object):
	"""An abstract base class for mock auth server, key server and
	app server. The primary reason for this class to exist is so the
	constructor can find an available port for the server to run and
	save that port & associated socket object in the socket and
	port properties."""

	def __init__(self):
		"""Opens a random but available socket and assigns it to the
		socket property. The socket's port is also assigned to the
		port property."""
		object.__init__(self)

		[self.socket] = tornado.netutil.bind_sockets(
			0,
			"localhost",
			family=socket.AF_INET)
		self.port = self.socket.getsockname()[1]

#-------------------------------------------------------------------------------

class AppServerRequestHandler(tornado.web.RequestHandler):
	"""Tornado request handler for use by the mock app server. This request
	handler only implements HTTP GET."""

	def _save_authorization_header_value(self):
		TestCase.authorization_header_in_request_to_app_server = \
			self.request.headers.get("Authorization", None)

	def get(self):
		"""Implements HTTP GET for the mock app server."""
		TestCase.app_server_received_get = True
		self._save_authorization_header_value()
		self.set_status(httplib.OK)

	def post(self):
		"""Implements HTTP POST for the mock app server."""
		TestCase.app_server_received_post = True
		self._save_authorization_header_value()
		self.set_status(httplib.OK)

	def put(self):
		"""Implements HTTP PUT for the mock app server."""
		TestCase.app_server_received_put = True
		self._save_authorization_header_value()
		self.set_status(httplib.OK)

	def delete(self):
		"""Implements HTTP DELETE for the mock app server."""
		TestCase.app_server_received_delete = True
		self._save_authorization_header_value()
		self.set_status(httplib.OK)

#-------------------------------------------------------------------------------

class AppServer(Server):
	"""The mock app server."""

	def __init__(self):
		"""Creates an instance of the mock app server and starts the
		server listenting on a random, available port."""
		Server.__init__(self)

		handlers=[(r".*", AppServerRequestHandler)]
		app = tornado.web.Application(handlers=handlers)
		http_server = tornado.httpserver.HTTPServer(app)
		http_server.add_sockets([self.socket])

#-------------------------------------------------------------------------------

class KeyServerRequestHandler(tornado.web.RequestHandler):
	"""Tornado request handler for use by the mock key server. This request
	handler only implements HTTP GET since that's the only type of request the
	auth server issues to the key server."""

	def get(self):
		"""Implements HTTP GET for the mock key server."""
		_logger.info(
			"Mock Key Server GET %s",
			self.request.uri)
		uri_reg_ex = re.compile(
			'^/v1\.0/creds/(?P<mac_key_identifier>.+)$',
			re.IGNORECASE )
		match = uri_reg_ex.match(self.request.uri)
		if not match:
			TestCase._mac_key_identifier_in_key_server_request = None
			self.set_status(httplib.BAD_REQUEST)
		else:
			assert 0 == match.start()
			assert len(self.request.uri) == match.end()
			assert 1 == len(match.groups())
			mac_key_identifier = match.group("mac_key_identifier")
			assert mac_key_identifier is not None
			assert 0 < len(mac_key_identifier)

			TestCase._mac_key_identifier_in_key_server_request = mac_key_identifier

			status = TestCase.status_code_of_response_to_key_server_request or httplib.OK
			self.set_status(status)

			if status == httplib.OK:
				dict = TestCase.body_of_response_to_key_server_request \
					or \
					{
						"is_deleted": False,
						"mac_algorithm": TestCase.mac_algorithm_response_to_key_server_request,
						"mac_key": TestCase.mac_key_in_response_to_key_server_request,
						"mac_key_identifier": mac_key_identifier,
						"owner": TestCase.owner_in_response_to_key_server_request or str(uuid.uuid4()),
					}
				body = json.dumps(dict)
				self.write(body)

				self.set_header(
					TestCase.content_type_of_response_to_key_server_request
					or
					"Content-Type", "application/json; charset=utf8")

#-------------------------------------------------------------------------------

class KeyServer(Server):
	"""The mock key server."""

	def __init__(self):
		"""Creates an instance of the mock key server and starts the
		server listenting on a random, available port."""
		Server.__init__(self)

		handlers=[(r".*", KeyServerRequestHandler)]
		app = tornado.web.Application(handlers=handlers)
		http_server = tornado.httpserver.HTTPServer(app)
		http_server.add_sockets([self.socket])

#-------------------------------------------------------------------------------

class AuthenticationServer(Server):
	"""Mock authentication server."""

	def __init__(self, key_server, app_server, app_server_auth_method):
		"""Creates an instance of the auth server and starts the
		server listenting on a random, available port."""
		Server.__init__(self)

		auth_server.key_server = "localhost:%d" % key_server.port
		auth_server.app_server = "localhost:%d" % app_server.port
		auth_server.app_server_auth_method = app_server_auth_method
		auth_server.include_auth_failure_detail = True

		http_server = tornado.httpserver.HTTPServer(auth_server._tornado_app)
		http_server.add_sockets([self.socket])

#-------------------------------------------------------------------------------

class IOLoop(threading.Thread):
	"""This class makes it easy for a test case's `setUpClass()` to start
	a Tornado io loop on the non-main thread so that the io loop, auth server
	key server and app server can operate 'in the background' while the
	unit test runs on the main thread."""

	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True

	def run(self):
		tornado.ioloop.IOLoop.instance().start()

	def stop(self):
		tornado.ioloop.IOLoop.instance().stop()

#-------------------------------------------------------------------------------

class TestCase(unittest.TestCase):
	
	"""When KeyServerRequestHandler's get() is given a valid
	mac key identifier, _mac_key_identifier_in_key_server_request
	is set to the mac key identifier in the handler.
	See TestCase's assertMACKeyIdentifierInKeyServerRequest()
	for when _mac_key_identifier_in_key_server_request is used."""
	_mac_key_identifier_in_key_server_request = None

	"""..."""
	status_code_of_response_to_key_server_request = None

	"""..."""
	content_type_of_response_to_key_server_request = None

	"""..."""
	body_of_response_to_key_server_request = None

	"""..."""
	mac_key_in_response_to_key_server_request = None

	"""..."""
	mac_algorithm_response_to_key_server_request = None

	"""When the mock key server responds to the auth server's request
	for credentials, ```owner_in_response_to_key_server_request```
	is used for the owner attribute."""
	owner_in_response_to_key_server_request = None

	"""When the auth server forwards a request to the app server the
	request's authorization header contained the value found
	in '''authorization_header_in_request_to_app_server```."""
	authorization_header_in_request_to_app_server = None

	"""When the app server recieves a GET it sets
	```app_server_received_post``` to True."""
	app_server_received_get = None

	"""When the app server recieves a POST it sets
	```app_server_received_post``` to True."""
	app_server_received_post = None

	"""When the app server recieves a PUT it sets
	```app_server_received_post``` to True."""
	app_server_received_put = None

	"""When the app server recieves a DELETE it sets
	```app_server_received_delete``` to True."""
	app_server_received_delete = None

	"""When the app server recieves a HEAD it sets
	```app_server_received_head``` to True."""
	app_server_received_head = None

	"""When the app server recieves a OPTIONS it sets
	```app_server_received_options``` to True."""
	app_server_received_options = None

	def setUp(self):
		unittest.TestCase.setUp(self)
		TestCase._mac_key_identifier_in_key_server_request = None
		TestCase.status_code_of_response_to_key_server_request = None
		TestCase.content_type_of_response_to_key_server_request = None
		TestCase.body_of_response_to_key_server_request = None
		TestCase.mac_key_in_response_to_key_server_request = None
		TestCase.mac_algorithm_response_to_key_server_request = None
		TestCase.owner_in_response_to_key_server_request = None
		TestCase.authorization_header_in_request_to_app_server = None
		TestCase.app_server_received_get = False
		TestCase.app_server_received_post = False
		TestCase.app_server_received_put = False
		TestCase.app_server_received_delete = False
		TestCase.app_server_received_head = False
		TestCase.app_server_received_options = False

	def assertIsJsonUtf8ContentType(self, content_type):
		"""Allows the caller to assert if ```content_type```
		is valid for specifying utf8 json content in an http header. """
		self.assertIsNotNone(content_type)
		json_utf8_content_type_reg_ex = re.compile(
			"^\s*application/json;\s+charset\=utf-{0,1}8\s*$",
			re.IGNORECASE )
		self.assertIsNotNone(json_utf8_content_type_reg_ex.match(content_type))

	def assertMACKeyIdentifierInKeyServerRequest(self, mac_key_identifier):
		"""The unit test that was just run caused the authentication server
		to call out (perhaps) to the key server. The authentication server
		made this call with a particular MAC key identifier. This method
		allows to caller to assert which MAC key identifier was sent to the
		key server."""
		if mac_key_identifier is None:
			self.assertIsNone(TestCase._mac_key_identifier_in_key_server_request)
		else:
			self.assertEqual(
				TestCase._mac_key_identifier_in_key_server_request,
				mac_key_identifier)

	def assertAuthorizationHeaderInAppServerRequest(
		self,
		expected_auth_method,
		expected_owner,
		expected_id):
		"""The unit test that was just run caused the authentication server
		to forward a request to the app server. The authentication server
		made this call with a particular authorization header. This method
		allows to caller to assert that the format and content of the authorization
		header was as expected."""
		self.assertIsNotNone(TestCase.authorization_header_in_request_to_app_server)
		reg_ex = re.compile(
			'^\s*(?P<auth_method>[^\s]+)\s+(?P<owner>[^\s]+)\s+(?P<id>[^\s]+)\s*$$',
			re.IGNORECASE )
		match = reg_ex.match(TestCase.authorization_header_in_request_to_app_server)
		self.assertIsNotNone(match)
		assert 0 == match.start()
		assert len(TestCase.authorization_header_in_request_to_app_server) == match.end()
		assert 3 == len(match.groups())
		auth_method = match.group("auth_method")
		assert auth_method is not None
		assert 0 < len(auth_method)
		owner = match.group("owner")
		assert owner is not None
		assert 0 < len(owner)
		id = match.group("id")
		assert id is not None
		assert 0 < len(id)
		self.assertEqual(auth_method, expected_auth_method)
		self.assertEqual(owner, expected_owner)
		self.assertEqual(id, expected_id)

	def assertAppServerRequest(self, get=False, post=False, delete=False, put=False, head=False, options=False):
		"""The unit test that was just run caused the authentication server
		to forward a request to the app server. This method allows the caller
		to assert that the app server recieved the correct request."""
		self.assertEqual(TestCase.app_server_received_get, get)
		self.assertEqual(TestCase.app_server_received_post, post)
		self.assertEqual(TestCase.app_server_received_put, put)
		self.assertEqual(TestCase.app_server_received_delete, delete)
		self.assertEqual(TestCase.app_server_received_head, head)
		self.assertEqual(TestCase.app_server_received_options, options)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	pass

#------------------------------------------------------------------- End-of-File
