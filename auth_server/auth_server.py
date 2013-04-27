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
import tornado.web
import jsonschema

from clparser import CommandLineParser
import tsh

#-------------------------------------------------------------------------------

_logger = logging.getLogger("AUTHSERVER_%s" % __name__)

#-------------------------------------------------------------------------------

__version__ = "1.0"

#-------------------------------------------------------------------------------

"""Once a request has been authenticated, the request is forwarded
to the app server as defined by this host:port combination."""
app_server = None

"""This host:port combination define the location of the key server."""
key_server = None

"""Once the auth server has verified the sender's identity the request
is forwarded to the app server. The forward to the app server does not
contain the original request's HTTP Authorization header but instead
uses the authorization method described by ```app_server_auth_method```
and the the credential's owner."""
app_server_auth_method = "DAS"

#-------------------------------------------------------------------------------

class AsyncCredsRetriever(object):
	"""Wraps the gory details of async crednetials retrieval."""

	def fetch(self, callback, mac_key_identifier):
		"""Retrieve the credentials for ```mac_key_identifier```
		and when done call ```callback```."""

		self._callback = callback
		self._mac_key_identifier = mac_key_identifier

		url = "http://%s/v1.0/mac_creds/%s" % (
			key_server,
			self._mac_key_identifier)
		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(
			tornado.httpclient.HTTPRequest( 
				url=url,
				method="GET",
				follow_redirects=False),
			callback=self._my_callback)

	def _my_callback(self, response):
		"""Called when request to the key server returns."""
		if response.code != httplib.OK:
			self._callback(False, self._mac_key_identifier)
			return

		if not self._extract_mac_credentials_from_key_server_response(response):
			self._callback(False, self._mac_key_identifier)
			return

		self._callback(
			True,
			self._mac_key_identifier,
			False, # is deleted
			self._key_server_mac_algorithm,
			self._key_server_mac_key,
			"dave")

	def _extract_mac_credentials_from_key_server_response(self, response):
		schema = {
			"type" : "object",
			"properties" : {
				"is_deleted" : {"type" : "string"},
				"mac_algorithm" : {"type" : "string"},
				"mac_key" : {"type" : "string"},
				"mac_key_identifier" : {"type" : "string"},
				"owner" : {"type" : "string"},
			},
		}
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
			self._mac_key_identifier,
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

		if self._key_server_mac_key_identifier != self._mac_key_identifier:
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

#-------------------------------------------------------------------------------

class AuthRequestHandler(tornado.web.RequestHandler):

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

	def _extract_authorization_header_value(self):
		authorization_header_value = self.request.headers.get("Authorization", None)
		if authorization_header_value is None:
			return False
		
		reg_ex = re.compile(
			'^\s*MAC\s+id\s*\=\s*"(?P<id>[^"]+)"\s*\,\s*ts\s*\=\s*"(?P<ts>[^"]+)"\s*\,\s*nonce\s*\=\s*"(?P<nonce>[^"]+)"\s*\,\s*ext\s*\=\s*"(?P<ext>[^"]*)"\s*\,\s*mac\s*\=\s*"(?P<mac>[^"]+)"\s*$',
			re.IGNORECASE)
		match = reg_ex.match(authorization_header_value)
		if not match:
			_logger.info(
				"Invalid format for authorization header '%s'",
				authorization_header_value)
			return False
		_logger.info(
			"Valid format for authorization header '%s'",
			authorization_header_value)

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

		self._auth_header_mac = match.group("mac")
		assert self._auth_header_mac is not None
		assert 0 < len(self._auth_header_mac)

		return True

	def _on_async_creds_retriever_done(
		self,
		is_ok,
		mac_key_identifier,
		is_deleted=None,
		mac_algorithm=None,
		mac_key=None,
		owner=None):

		if not is_ok:
			_logger.error(
				"No MAC credentials found for '%s'",
				self.request.uri)
			self.set_status(httplib.UNAUTHORIZED)
			self.finish()
			return

		# :TODO: now that we've got the MAC credentials, use them to
		# confirm the caller's identity
		_logger.info(
			"Authorization successful for '%s'",
			self.request.uri)

		headers = tornado.httputil.HTTPHeaders(self.request.headers)
		headers["Authorization"] = '%s %s' % (
			app_server_auth_method,
			owner)

		body = None
		if 0 < self.request.headers.get("Content-Length", 0):
			body = self.request.body

		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(
			tornado.httpclient.HTTPRequest( 
				url="http://%s%s" % (app_server, self.request.uri),
				method=self.request.method, 
				body=body,
				headers=headers,
				follow_redirects=False),
			callback=self._handle_app_server_response)

	@tornado.web.asynchronous
	def _handle_request(self):
		if not self._extract_authorization_header_value():
			self.set_status(httplib.UNAUTHORIZED)
			self.finish()
			return

		acr = AsyncCredsRetriever()
		acr.fetch(self._on_async_creds_retriever_done, self._auth_header_id)

	def post(self):
		self._handle_request()

	def get(self):
		self._handle_request()

	def put(self):
		self._handle_request()

	def delete(self):
		self._handle_request()

#-------------------------------------------------------------------------------

# _tornado_app simplifies construction of testing infrastructure
_tornado_app = tornado.web.Application(handlers=[(r".*", AuthRequestHandler),])

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	clp = CommandLineParser()
	(clo, cla) = clp.parse_args()

	tsh.install_handler()

	logging.basicConfig(level=clo.logging_level)

	_logger.info(
		"Auth Server listening on %d using Key Server '%s' and App Server '%s'",
		clo.port,
		clo.key_server,
		clo.app_server)

	key_server = clo.key_server
	app_server = clo.app_server
	auth_method = clo.app_server_auth_method

	http_server = tornado.httpserver.HTTPServer(_tornado_app)
	http_server.listen(clo.port)
	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
