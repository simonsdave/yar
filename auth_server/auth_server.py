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
import hashlib

import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web
import jsonschemas

from clparser import CommandLineParser
import tsh
import trhutil
import strutil
import mac

#-------------------------------------------------------------------------------

_logger = logging.getLogger("AUTHSERVER.%s" % __name__)
_logger.addHandler(logging.NullHandler())

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

"""To help prevent reply attacks the timestamp of all requests can
be no older than ```maxage``` seconds before the current timestamp."""
maxage = 30

#-------------------------------------------------------------------------------

class AsyncCredsRetriever(object):
	"""Wraps the gory details of async crednetials retrieval."""

	def fetch(self, callback, mac_key_identifier):
		"""Retrieve the credentials for ```mac_key_identifier```
		and when done call ```callback```."""

		self._callback = callback
		self._mac_key_identifier = mac_key_identifier

		url = "http://%s/v1.0/creds/%s" % (
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

		response = trhutil.Response(response)
		body = response.get_json_body(jsonschemas.key_server_get_creds_response)
		if body is None:
			self._callback(False, self._mac_key_identifier)
			return

		_logger.info(
			"For mac key identifier '%s' retrieved credentials '%s'",
			self._mac_key_identifier,
			body)

		self._callback(
			True,
			mac.MACKeyIdentifier(self._mac_key_identifier),
			body["is_deleted"],
			body["mac_algorithm"],
			mac.MACKey(body["mac_key"]),
			body["owner"])

#-------------------------------------------------------------------------------

class AuthRequestHandler(trhutil.RequestHandler):

	def _set_debug_header(self, name, value):
		"""Called by ```_set_debug_headers()``` to actually
		set the HTTP header called ```name``` of ```value```.
		This method is entirely about making the implementation
		of ```_set_debug_headers()``` cleaner."""
		value = strutil.make_http_header_value_friendly(value)
		self.set_header(name, value)

	def _set_debug_headers(
		self,
		mac_key_identifier,
		mac_key,
		mac_algorithm,
		host,
		port,
		content_type,
		http_method,
		uri,
		body,
		ts,
		nonce,
		ext):
		"""When an authorization failure occurs it can be super hard
		to figure out the root cause of the error. This method is called
		on authorization failure and, if logging is set to at least debug,
		a whole series of HTTP headers are set to return the core elements
		that are used to generate the HMAC."""

		if not _logger.isEnabledFor(logging.INFO):
			return

		self._set_debug_header("X-AUTH-SERVER-MAC-KEY-IDENTIFIER", mac_key_identifier)
		self._set_debug_header("X-AUTH-SERVER-MAC-KEY", mac_key)
		self._set_debug_header("X-AUTH-SERVER-MAC-ALGORITHM", mac_algorithm)
		self._set_debug_header("X-AUTH-SERVER-HOST", host)
		self._set_debug_header("X-AUTH-SERVER-PORT", port)
		self._set_debug_header("X-AUTH-SERVER-CONTENT-TYPE", content_type)
		self._set_debug_header("X-AUTH-SERVER-REQUEST-METHOD", http_method)
		self._set_debug_header("X-AUTH-SERVER-URI", uri)
		if body is not None:
			self._set_debug_header("X-AUTH-SERVER-BODY-SHA1", hashlib.sha1(body).hexdigest())
			self._set_debug_header("X-AUTH-SERVER-BODY-LEN", len(body))
			self._set_debug_header("X-AUTH-SERVER-BODY", body)
		self._set_debug_header("X-AUTH-SERVER-TIMESTAMP", ts)
		self._set_debug_header("X-AUTH-SERVER-NONCE", nonce)
		self._set_debug_header("X-AUTH-SERVER-EXT", ext)

	def _on_app_server_done(self, response):
		if response.error:
			self.set_status(httplib.INTERNAL_SERVER_ERROR) 
		else:
			self.set_status(response.code) 
			for header_name in response.headers.keys():
				self.set_header(header_name, response.headers[header_name]) 
			if 0 < response.headers.get("Content-Length", 0):
				self.write(response.body) 
		self.finish()

	def _on_async_creds_retriever_done(
		self,
		is_ok,
		mac_key_identifier,
		is_deleted=None,
		mac_algorithm=None,
		mac_key=None,
		owner=None):

		if not is_ok:
			_logger.info(
				"No MAC credentials found for '%s'",
				self.request.full_url())
			self.set_status(httplib.UNAUTHORIZED)
			self.finish()
			return

		(host, port) = self.get_request_host_and_port("localhost", 80)
		content_type = self.request.headers.get("Content-type", None)
		body = self.get_request_body_if_exists(None)
		ext = mac.Ext.generate(content_type, body)
		normalized_request_string = mac.NormalizedRequestString.generate(
			self._auth_hdr_val.ts,
			self._auth_hdr_val.nonce,
			self.request.method,
			self.request.uri,
			host,
			port,
			ext)

		macs_equal = self._auth_hdr_val.mac.verify(
			mac_key,
			mac_algorithm,
			normalized_request_string)
		if not macs_equal:
			_logger.info(
				"For '%s' using MAC key identifier '%s' MAC in request '%s' doesn't match computed MAC",
				self.request.full_url(),
				mac_key_identifier,
				self._auth_hdr_val.mac)
			self._set_debug_headers(
				mac_key_identifier,
				mac_key,
				mac_algorithm,
				host,
				port,
				content_type,
				self.request.method,
				self.request.uri,
				body,
				self._auth_hdr_val.ts,
				self._auth_hdr_val.nonce,
				ext)
			self.set_status(httplib.UNAUTHORIZED)
			self.finish()
			return

		_logger.info(
			"Authorization successful for '%s' and MAC '%s'",
			self.request.full_url(),
			self._auth_hdr_val.mac)

		headers = tornado.httputil.HTTPHeaders(self.request.headers)
		headers["Authorization"] = "%s %s %s" % (
			app_server_auth_method,
			owner,
			mac_key_identifier)

		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(
			tornado.httpclient.HTTPRequest( 
				url="http://%s%s" % (app_server, self.request.uri),
				method=self.request.method, 
				body=body,
				headers=headers,
				follow_redirects=False),
			callback=self._on_app_server_done)

	def _handle_request(self):
		"""```get()```, ```post()```, ```put()```, ```options()```,
		```delete()``` and ```head()``` requests are all forwarded
		to this method which is responsible for kicking off the core
		authentication logic."""
		auth_hdr_val = self.request.headers.get("Authorization", None)
		self._auth_hdr_val = mac.AuthHeaderValue.parse(auth_hdr_val)
		if self._auth_hdr_val is None:
			self.set_status(httplib.UNAUTHORIZED)
			self.finish()
			return

		# confirm the request isn't old which is important in protecting
		# against reply attacks - also requests with timestamps in the
		# future are also 
		now = mac.Timestamp.generate()
		age = int(now) - int(self._auth_hdr_val.ts)
		if age < 0:
			# :TODO: timestamp in the future - bad - clocks out of sync?
			# do we want to allow clocks to be a wee bit ouf of sync?
			self.set_status(httplib.UNAUTHORIZED)
			self.finish()
			return

		if maxage < age:
			self.set_status(httplib.UNAUTHORIZED)
			self.finish()
			return

		# basic request looks good = authentication header found and format
		# is valid plus the request's timestamp is recent. next steps is
		# to retrieve the credentials associated with the request's
		# mac key identifier and confirm the request's MAC is valid thus
		# confirming the sender's identity
		acr = AsyncCredsRetriever()
		acr.fetch(
			self._on_async_creds_retriever_done,
			self._auth_hdr_val.mac_key_identifier)

	@tornado.web.asynchronous
	def get(self):
		self._handle_request()

	@tornado.web.asynchronous
	def post(self):
		self._handle_request()

	@tornado.web.asynchronous
	def put(self):
		self._handle_request()

	@tornado.web.asynchronous
	def delete(self):
		self._handle_request()

	@tornado.web.asynchronous
	def head(self):
		self._handle_request()

	@tornado.web.asynchronous
	def options(self):
		self._handle_request()

#-------------------------------------------------------------------------------

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
	maxage = clo.maxage

	http_server = tornado.httpserver.HTTPServer(_tornado_app)
	http_server.listen(clo.port)
	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
