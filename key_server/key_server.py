#!/usr/bin/env python
"""This module contains the core key server logic."""

import httplib
import re
import json
import uuid
import logging

import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web

from clparser import CommandLineParser
import tsh

#-------------------------------------------------------------------------------

"""Format of this string is host:port/database. It's used to construct
a URL when talking to the key store."""
_key_store = "localhost:5984/macaa"

#-------------------------------------------------------------------------------

__version__ = "1.0"

#-------------------------------------------------------------------------------

_logger = logging.getLogger("KEYSERVER_%s" % __name__)

#-------------------------------------------------------------------------------

class StatusRequestHandler(tornado.web.RequestHandler):

	def get(self):
		status = {
			"status": "ok",
			"version": __version__,
		}
		self.write(status)

#-------------------------------------------------------------------------------

class AsnycCredsCreator(object):

	def _uuid(self):
		return str(uuid.uuid4()).replace("-","")

	def create(self, owner, callback):

		self._callback = callback

		self._creds = {
		   "owner": owner,
		   "mac_key_identifier": self._uuid(),
		   "mac_key": self._uuid(),
		   "mac_algorithm": "hmac-sha-1",
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

	def fetch(self, callback, mac_key_identifier=None, owner=None):
		object.__init__(self)

		self._callback = callback

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
				
		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(
			tornado.httpclient.HTTPRequest(
				url,
				method="GET",
				follow_redirects=False),
			callback=self._my_callback)

	def _my_callback(self, response):
		if response.code != httplib.OK:
			self._callback(None)
			return

		body_as_dict = json.loads(response.body)
		if 'rows' in body_as_dict:
			rv = []
			for row in body_as_dict['rows']:
				doc = row['value']
				# :TODO: filter out the CouchDB specific attributes that should
				# not flow outside of the key server
				rv.append(doc)
		else:
			# :TODO: filter out the CouchDB specific attributes that should
			# not flow outside of the key server
			rv = body_as_dict

		self._callback(rv)

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
			mac_key_identifier=mac_key_identifier)

#-------------------------------------------------------------------------------

class RequestHandler(tornado.web.RequestHandler):

	def _async_creds_retriever_callback_for_get(self, creds):
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
			self._async_creds_retriever_callback_for_get,
			mac_key_identifier=mac_key_identifier,
			owner=self.get_argument("owner", None))

	def _is_json_utf8_content_type(self):
		content_type = self.request.headers.get("content-type", None)
		if content_type is None:
			return False
		json_utf8_content_type_reg_ex = re.compile(
			"^\s*application/json;\s+charset\=utf-{0,1}8\s*$",
			re.IGNORECASE )
		if not json_utf8_content_type_reg_ex.match(content_type):
			return False
		return True

	def _get_owner_from_request_body(self):
		# :TODO: wrap this up in a "_get_json_body_as_dict()"
		if not self._is_json_utf8_content_type():
			return None

		body = self.request.body
		if body is None:
			return None

		try:
			body_as_dict = json.loads(body)
		except:
			return None

		if "owner" not in body_as_dict:
			return None
		owner = body_as_dict["owner"]

		owner = owner.strip()
		if 0 == len(owner):
			return None

		return owner

	def _on_async_creds_create_done(self, creds):
		if creds is None:
			self.set_status(httplib.INTERNAL_SERVER_ERROR)
			self.finish()
			return

		location_url = "%s/%s" % (
			self.request.full_url(),
			creds["mac_key_identifier"])
		self.set_header("Location", location_url)
		self.set_status(httplib.CREATED)
		self.finish()

	@tornado.web.asynchronous
	def post(self, mac_key_identifer=None):
		if mac_key_identifer is not None:
			self.set_status(httplib.METHOD_NOT_ALLOWED)
			self.finish()
			return

		owner = self._get_owner_from_request_body()
		if owner is None:
			self.set_status(httplib.BAD_REQUEST)
			self.finish()
			return

		acc = AsnycCredsCreator()
		acc.create(owner, self._on_async_creds_create_done)

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
	(r"/v1.0/mac_creds(?:/([^/]+))?", RequestHandler),
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
