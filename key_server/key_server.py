#!/usr/bin/env python
"""This module contains the core key server logic."""

import httplib
import re
import json
import logging

import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web

from clparser import CommandLineParser
import tsh
import trhutil
import jsonschemas
import mac

#-------------------------------------------------------------------------------

"""Format of this string is host:port/database. It's used to construct
a URL when talking to the key store."""
_key_store = "localhost:5984/creds"

#-------------------------------------------------------------------------------

__version__ = "1.0"

#-------------------------------------------------------------------------------

_logger = logging.getLogger("KEYSERVER.%s" % __name__)

#-------------------------------------------------------------------------------

class StatusRequestHandler(trhutil.RequestHandler):

	def get(self):
		status = {
			"status": "ok",
			"version": __version__,
		}
		self.write(status)

#-------------------------------------------------------------------------------

class AsnycCredsCreator(object):

	def create(self, owner, callback):

		self._callback = callback

		self._creds = {
		   "owner": owner,
		   "mac_key_identifier": mac.MACKeyIdentifier.generate(),
		   "mac_key": mac.MACKey.generate(),
		   "mac_algorithm": mac.MAC.algorithm,
		   "type": "cred_v1.0",
		   "is_deleted": False,
		}
		headers = {
			"Content-Type": "application/json; charset=utf8",
			"Accept": "application/json",
			"Accept-Encoding": "charset=utf8"
		}
		url = "http://%s/%s" % (
			_key_store,
			self._creds["mac_key_identifier"])
		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(
			tornado.httpclient.HTTPRequest(
				url,
				method="PUT",
				headers=tornado.httputil.HTTPHeaders(headers),
				body=json.dumps(self._creds)),
			callback=self._my_callback)

	def _my_callback(self, response):
		if response.code != httplib.CREATED:
			self._callback(None)
			return	

		self._callback(self._creds)

#-------------------------------------------------------------------------------

class AsyncCredsRetriever(object):

	def fetch(
		self,
		callback,
		mac_key_identifier=None,
		owner=None,
		is_filter_out_deleted=True,
		is_filter_out_non_model_properties=False):

		object.__init__(self)

		self._callback = callback
		self._is_filter_out_non_model_properties = is_filter_out_non_model_properties
		self._is_filter_out_deleted = is_filter_out_deleted

		if mac_key_identifier:
			url = "http://%s/%s" % (_key_store, mac_key_identifier)
		else:
			if owner:
				url = 'http://%s/_design/creds/_view/by_owner?startkey="%s"&endkey="%s"' % (
					_key_store,
					owner,
					owner)
			else:
				url = "http://%s/_design/creds/_view/all" % _key_store
				
		headers = {
			"Accept": "application/json",
			"Accept-Encoding": "charset=utf8",
		}
		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(
			tornado.httpclient.HTTPRequest(
				url,
				method="GET",
				headers=headers,
				follow_redirects=False),
			callback=self._my_callback)

	def _my_callback(self, response):
		response = trhutil.Response(response)
		body = response.get_json_body()
		if not body:
			self._callback(None)
			return

		if 'rows' in body:
			rv = []
			for row in body['rows']:
				doc = row['value']
				if doc.get("is_deleted", False):
					if self._is_filter_out_deleted:
						continue	
				if self._is_filter_out_non_model_properties:
					doc = self._filter_out_non_model_properties(doc)
				rv.append(doc)
		else:
			if body.get("is_deleted", False) and self._is_filter_out_deleted:
				rv = None
			else:
				if self._is_filter_out_non_model_properties:
					body = self._filter_out_non_model_properties(body)
				rv = body

		self._callback(rv)

	def _filter_out_non_model_properties(self, dict):
		rv = {}
		for key in ["is_deleted","mac_algorithm","mac_key","mac_key_identifier","owner"]:
			if key in dict:
				rv[key] = dict[key]
		return rv

#-------------------------------------------------------------------------------

class AsyncCredsDeleter(object):

	def _on_response_from_key_store_to_put_for_delete(self, response):
		self._callback(response.code == httplib.CREATED)

	def _on_async_creds_retriever_done(self, creds):
		if creds is None:
			self._callback(False)
			return

		if creds.get("is_deleted", False):
			self._callback(True)
			return

		creds["is_deleted"] = True

		headers = {
			"Content-Type": "application/json; charset=utf8",
			"Accept": "application/json",
			"Accept-Encoding": "charset=utf8",
		}
		url = "http://%s/%s" % (
			_key_store,
			creds["mac_key_identifier"])
		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(
			tornado.httpclient.HTTPRequest(
				url,
				method="PUT",
				headers=tornado.httputil.HTTPHeaders(headers),
				body=json.dumps(creds)),
			callback=self._on_response_from_key_store_to_put_for_delete)
			
	def delete(self, mac_key_identifier, callback):
		self._callback = callback

		acr = AsyncCredsRetriever()
		acr.fetch(
			self._on_async_creds_retriever_done,
			mac_key_identifier=mac_key_identifier,
			is_filter_out_deleted=False)

#-------------------------------------------------------------------------------

class RequestHandler(trhutil.RequestHandler):

	def _on_async_creds_retrieve_done(self, creds):
		if creds is None:
			self.set_status(httplib.NOT_FOUND)
			self.finish()
			return

		self.write(json.dumps(creds))
		self.set_header("Content-Type", "application/json; charset=utf8") 
		self.finish()

	@tornado.web.asynchronous
	def get(self, mac_key_identifier=None):
		acr = AsyncCredsRetriever()
		acr.fetch(
			self._on_async_creds_retrieve_done,
			mac_key_identifier=mac_key_identifier,
			owner=self.get_argument("owner", None),
			is_filter_out_deleted=False if self.get_argument("deleted", None) else True,
			is_filter_out_non_model_properties=True)

	def _on_async_creds_create_done(self, creds):
		if creds is None:
			self.set_status(httplib.INTERNAL_SERVER_ERROR)
			self.finish()
			return

		location_url = "%s/%s" % (
			self.request.full_url(),
			creds["mac_key_identifier"])
		self.set_header("Content-Location", location_url)
		self.set_status(httplib.CREATED)
		self.finish()

	@tornado.web.asynchronous
	def post(self, mac_key_identifer=None):
		if mac_key_identifer is not None:
			self.set_status(httplib.METHOD_NOT_ALLOWED)
			self.finish()
			return

		body = self.get_json_request_body(
			None,
			jsonschemas.key_server_create_creds_request)
		if not body:
			self.set_status(httplib.BAD_REQUEST)
			self.finish()
			return

		acc = AsnycCredsCreator()
		acc.create(
			body["owner"],
			self._on_async_creds_create_done)

	def _on_async_creds_delete_done(self, isok):
		if isok is None:
			status = httplib.INTERNAL_SERVER_ERROR
		else:
			if isok:
				status = httplib.OK
			else:
				status = httplib.NOT_FOUND

		self.set_status(status)
		self.finish()

	@tornado.web.asynchronous
	def delete(self, mac_key_identifier=None):
		if mac_key_identifier is None:
			self.set_status(httplib.METHOD_NOT_ALLOWED)
			self.finish()
			return

		acd = AsyncCredsDeleter()
		acd.delete(
			mac_key_identifier,
			self._on_async_creds_delete_done)

#-------------------------------------------------------------------------------

_tornado_handlers = [
	(r"/(?:status)?", StatusRequestHandler),
	(r"/v1.0/creds(?:/([^/]+))?", RequestHandler),
]

_tornado_app = tornado.web.Application(handlers=_tornado_handlers)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	clp = CommandLineParser()
	(clo, cla) = clp.parse_args()

	logging.basicConfig(level=clo.logging_level)

	tsh.install_handler()

	_key_store = clo.key_store

	_logger.info(
		"Key server listening on %d and using key store '%s'",
		clo.port,
		clo.key_store)

	http_server = tornado.httpserver.HTTPServer(_tornado_app)
	http_server.listen(clo.port)

	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
