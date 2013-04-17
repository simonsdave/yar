#!/usr/bin/env python
"""This module contains the core logic for the authenication server.
The server uses implements MAC Access Authentication.

Key influencers for this module include [1]
[1]: https://groups.google.com/forum/?fromgroups=#!msg/python-tornado/TB_6oKBmdlA/Js9JoOcI6nsJ"""

#-------------------------------------------------------------------------------

import logging
import re
import json
import httplib

import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.options
import tornado.web

#-------------------------------------------------------------------------------

_logger = logging.getLogger("AUTHSERVER_%s" % __name__)

#-------------------------------------------------------------------------------

__version__ = "1.0"

#-------------------------------------------------------------------------------

class StatusRequestHandler(tornado.web.RequestHandler):
	"""This class is responsible for handling HTTP GET requests
	against the auth server's status resource."""

	def get(self):
		self.write({"status": "ok", "version": __version__})

#-------------------------------------------------------------------------------

class AuthRequestHandler(tornado.web.RequestHandler):

	"""Once a request has been authenticated, the request is forwarded
	to the app server as defined by this host:port combination."""
	app_server = None

	"""This host:port combination define the location of the key server."""
	key_server = None

	def _handle_app_server_response(self, response):
		if response.error:
			self.set_status(httplib.INTERNAL_SERVER_ERROR) 
		else:
			self.set_status(response.code) 
			for header_name in response.headers.keys():
				self.set_header(header_name, response.headers[header_name]) 
			if 0 < response.headers.get("Content-Length", 0):
				self.write(response.body) 
		self.finish()

	def _extract_mac_credentials_from_key_server_response(self, response):
		"""This method parses the response from the key server. The response
		is supposed to be a JSON document containing mac credentials."""
		if httplib.OK != response.code:
			_logger.info(
				"Failed to find mac credentials for MAC key identifier '%s'",
				self._auth_header_id)
			return False

		# :TODO: exepcting content-type to be JSON
		# :TODO: what happens if this is invalid JSON or not JSON at all?
		mac_credentials = json.loads(response.body)

		_logger.info(
			"For MAC key identifier '%s' retrieved '%s' from key server",
			self._auth_header_id,
			mac_credentials)

		# :TODO: be more paranoid in the code below ITO the contents of the JSON document

		self._key_server_mac_key_identifier = mac_credentials.get(
			"mac_key_identifier",
			None)
		if self._key_server_mac_key_identifier is None:
			_logger.error(
				"'mac_key_identifier' not found in mac credentials '%s'",
				mac_credentials)
			return False

		if self._key_server_mac_key_identifier != self._auth_header_id:
			_logger.error(
				"MAC key identifier '%s' expected but '%s' found",
				self._auth_header_id,
				self._key_server_mac_key_identifier)
			return False

		self._key_server_mac_key = mac_credentials.get("mac_key", None)
		if self._key_server_mac_key is None:
			_logger.error(
				"'mac_key' not found in mac credentials '%s'",
				mac_credentials)
			return False

		self._key_server_mac_algorithm = mac_credentials.get(
			"mac_algorithm",
			None)
		if self._key_server_mac_algorithm is None:
			_logger.error(
				"'mac_algorithm' not found in mac credentials '%s'",
				mac_credentials)
			return False

		valid_mac_algorithms = ["hmac-sha-1", "hmac-sha-256"]
		if self._key_server_mac_algorithm not in valid_mac_algorithms:
			_logger.error(
				"'%s' is not one of the support mac algorithms = '%s'",
				self._key_server_mac_algorithm,
				valid_mac_algorithms)
			return False

		return True

	def _handle_key_server_response(self, response):
		if not self._extract_mac_credentials_from_key_server_response(response):
			_logger.error(
				"No MAC credentials found for '%s'",
				response.request.url)
			self.set_status(httplib.UNAUTHORIZED)
			self.finish()
			return

		# :TODO: now that we've got the MAC credentials, use them to
		# confirm the caller's identity

		headers = tornado.httputil.HTTPHeaders(self.request.headers)
		headers["Authorization"] = 'VOYAGER id="%s"' % self._auth_header_id

		# required because self.request.body throws an exception
		# if there's no body in the request
		body = None
		if 0 < self.request.headers.get("Content-Length", 0):
			body = self.request.body

		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(
			tornado.httpclient.HTTPRequest( 
				url="http://%s%s" % (self.__class__.app_server, self.request.uri),
				method=self.request.method, 
				body=body,
				headers=headers,
				follow_redirects=False),
			callback=self._handle_app_server_response)

	# Authorization: MAC id="h480djs93hd8",
	#			         nonce="264095:dj83hs9s",
	#			         mac="SLDJd4mg43cjQfElUs3Qub4L6xE="

	def _extract_authorization_header_value(self):
		authorization_header_value = self.request.headers.get("Authorization", None)
		if authorization_header_value is None:
			return False
		
		reg_ex = re.compile(
			'^\s*MAC\s+id\s*\=\s*"(?P<id>[^"]+)"\s*\,\s*ts\s*\=\s*"(?P<ts>[^"]+)"\s*\,\s*nonce\s*\=\s*"(?P<nonce>[^"]+)"\s*\,\s*ext\s*\=\s*"(?P<ext>[^"]+)"\s*\,\s*mac\s*\=\s*"(?P<mac>[^"]+)"\s*$',
			re.IGNORECASE )
		match = reg_ex.match(authorization_header_value)
		if not match:
			return False

		assert 0 == match.start()
		assert len(authorization_header_value) == match.end()
		assert 5 == len(match.groups())

		self._auth_header_id = match.group("id")
		assert self._auth_header_id is not None
		assert 0 < len(self._auth_header_id)

		self._auth_header_ts = match.group("ts")
		assert self._auth_header_ts is not None
		assert 0 < len(self._auth_header_ts)

		self._auth_header_nonce = match.group("nonce")
		assert self._auth_header_nonce is not None
		assert 0 < len(self._auth_header_nonce)

		self._auth_header_ext = match.group("ext")
		assert self._auth_header_ext is not None
		assert 0 < len(self._auth_header_ext)

		self._auth_header_mac = match.group("mac")
		assert self._auth_header_mac is not None
		assert 0 < len(self._auth_header_mac)

		return True

	@tornado.web.asynchronous
	def _handle_request(self):
		if not self._extract_authorization_header_value():
			self.set_status(httplib.UNAUTHORIZED)
			self.finish()
			return

		url = "http://%s/v1.0/mac_creds/%s" % (
			self.__class__.key_server,
			self._auth_header_id)
		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(
			tornado.httpclient.HTTPRequest( 
				url=url,
				method="GET",
				follow_redirects=False),
			callback=self._handle_key_server_response)

	def post(self):
		self._handle_request()

	def get(self):
		self._handle_request()

	def put(self):
		self._handle_request()

	def delete(self):
		self._handle_request()

#-------------------------------------------------------------------------------

# _tornado_handlers simplifies the _tornado_app constructor
_tornado_handlers=[
	(r"/status", StatusRequestHandler),
	(r".*", AuthRequestHandler),
	]
# _tornado_app simplifies construction of testing infrastructure
_tornado_app = tornado.web.Application(handlers=_tornado_handlers)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	tornado.options.define(
		"port",
		default=8000,
		help="run on this port",
		type=int)
	tornado.options.define(
		"key_server",
		default="localhost:6969",
		help="key server's host:port",
		type=str)
	tornado.options.define(
		"app_server",
		default="localhost:8080",
		help="app server's host:port",
		type=str)
	tornado.options.parse_command_line()
	AuthRequestHandler.key_server = tornado.options.options.key_server
	AuthRequestHandler.app_server = tornado.options.options.app_server

	http_server = tornado.httpserver.HTTPServer(_tornado_app)
	http_server.listen(tornado.options.options.port)
	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
