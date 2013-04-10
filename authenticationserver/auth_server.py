#!/usr/bin/env python
"""This module contains the core logic for the authenication server.
The server uses implements MAC Access Authentication.

Key influencers for this module include [1]
[1]: https://groups.google.com/forum/?fromgroups=#!msg/python-tornado/TB_6oKBmdlA/Js9JoOcI6nsJ"""

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

class StatusRequestHandler(tornado.web.RequestHandler):

	def get(self):
		self.write({"status": "ok", "version": "1.0"})

#-------------------------------------------------------------------------------

class AuthRequestHandler(tornado.web.RequestHandler):

	app_server = None
	key_server = None

	def _handle_app_server_response(self, response):
		self.set_status(response.code) 
		for header_name in response.headers.keys():
			self.set_header(header_name, response.headers[header_name]) 
		if response.body: 
			self.write(response.body) 
		self.finish()

	def _extract_mac_credentials_from_key_server_response(self,response):
		"""This method parses the response from the key server. The response
		is supposed to be a JSON document containing mac credentials."""
		if httplib.OK != response.code:
			return False

		# :TODO: exepcting content-type to be JSON
		# :TODO: what happens if this is invalid JSON or not JSON at all?
		mac_credentials = json.loads(response.body)

		# :TODO: be more paranoid in the code below ITO the contents of the JSON document

		if "mac_key_identifier" not in mac_credentials:
			_logger.error(
				"'mac_key_identifier' not found in mac credentials '%s'",
				mac_credentials)
			return False
		self._key_server_mac_key_identifier = mac_credentials["mac_key_identifier"]
		assert self._key_server_mac_key_identifier is not None

		if self._key_server_mac_key_identifier != self._auth_header_id:
			_logger.error(
				"MAC key identifier '%s' expected but '%s' found",
				self._auth_header_id,
				self._key_server_mac_key_identifier)
			return False

		if "mac_key" not in mac_credentials:
			_logger.error(
				"'mac_key' not found in mac credentials '%s'",
				mac_credentials)
			return False
		self._key_server_mac_key = mac_credentials["mac_key"]
		assert self._key_server_mac_key is not None

		if "mac_algorithm" not in mac_credentials:
			_logger.error(
				"'mac_algorithm' not found in mac credentials '%s'",
				mac_credentials)
			return False
		self._key_server_mac_algorithm = mac_credentials["mac_algorithm"]
		assert self._key_server_mac_algorithm is not None

		if "issue_time" not in mac_credentials:
			_logger.error(
				"'issue_time' not found in mac credentials '%s'",
				mac_credentials)
			return False
		self._key_server_issue_time = mac_credentials["issue_time"]
		assert self._key_server_issue_time is not None

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

		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(
			tornado.httpclient.HTTPRequest( 
				url="http://%s%s" % (self.__class__.app_server, self.request.uri),
				method=self.request.method, 
				body=(self.request.body or None), 
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
			'^\s*MAC\s+id\s*\=\s*"(?P<id>[^"]+)"\s*\,\s*nonce\s*\=\s*"(?P<nonce>[^"]+)"\s*\,\s*mac\s*\=\s*"(?P<mac>[^"]+)"\s*$',
			re.IGNORECASE )
		match = reg_ex.match(authorization_header_value)
		if not match:
			return False

		assert 0 == match.start()
		assert len(authorization_header_value) == match.end()
		assert 3 == len(match.groups())
		self._auth_header_id = match.group("id")
		assert self._auth_header_id is not None
		assert 0 < len(self._auth_header_id)
		self._auth_header_nonce = match.group("nonce")
		assert self._auth_header_nonce is not None
		assert 0 < len(self._auth_header_nonce)
		self._auth_header_mac = match.group("mac")
		assert self._auth_header_mac is not None
		assert 0 < len(self._auth_header_mac)
		return True

	@tornado.web.asynchronous
	def _handle_request(self):
		"""This method is the key entry point for handling all get, post, delete
		and put requests."""
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
	RequestHandler.key_server = tornado.options.options.key_server
	RequestHandler.app_server = tornado.options.options.app_server

	http_server = tornado.httpserver.HTTPServer(_tornado_app)
	http_server.listen(tornado.options.options.port)
	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
