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
import jsonschemas

from clparser import CommandLineParser
import tsh
import trhutil
import mac

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
			self._mac_key_identifier,
			body["is_deleted"],
			body["mac_algorithm"],
			body["mac_key"],
			body["owner"])

#-------------------------------------------------------------------------------

class AuthRequestHandler(trhutil.RequestHandler):

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
			_logger.error(
				"No MAC credentials found for '%s'",
				self.request.uri)
			self.set_status(httplib.UNAUTHORIZED)
			self.finish()
			return

		content_type = self.request.headers.get("Content-type", None)
		body = self.get_request_body_if_exists(None)
		(host, port) = self.get_request_host_and_port("localhost", 80)
		normalized_request_string = mac.NormalizedRequestString(
			self._parsed_auth_header_value.ts,
			self._parsed_auth_header_value.nonce,
			self.request.method,
			self.request.uri,
			host,
			port,
			mac.Ext(content_type, body))
		my_mac = mac.MAC.compute(
			mac_key,
			mac_algorithm,
			normalized_request_string)

		if self._parsed_auth_header_value.mac != my_mac:
			_logger.error(
				"For '%s' MAC in request '%s' doesn't match computed MAC '%s'",
				self.request.uri,
				self._parsed_auth_header_value.mac,
				my_mac)
			self.set_status(httplib.UNAUTHORIZED)
			self.finish()
			return

		_logger.info(
			"Authorization successful for '%s' and MAC '%s'",
			self.request.full_url(),
			my_mac)

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

	@tornado.web.asynchronous
	def _handle_request(self):
		self._parsed_auth_header_value = mac.AuthHeaderValue.parse(
			self.request.headers.get("Authorization", None))
		if not self._parsed_auth_header_value:
			self.set_status(httplib.UNAUTHORIZED)
			self.finish()
			return

		acr = AsyncCredsRetriever()
		acr.fetch(
			self._on_async_creds_retriever_done,
			self._parsed_auth_header_value.mac_key_identifier)

	def get(self):
		self._handle_request()

	def post(self):
		self._handle_request()

	def put(self):
		self._handle_request()

	def delete(self):
		self._handle_request()

	def head(self):
		self._handle_request()

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

	http_server = tornado.httpserver.HTTPServer(_tornado_app)
	http_server.listen(clo.port)
	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
