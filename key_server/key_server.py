#!/usr/bin/env python
"""This module contains the core key server logic."""

import httplib
import re
import json
import uuid

import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web

import couchdb
import maccreds
from clparser import CommandLineParser

#-------------------------------------------------------------------------------

__version__ = "1.0"

#-------------------------------------------------------------------------------

class StatusHandler(tornado.web.RequestHandler):

	def get(self):
		status = {
			"status": "ok",
			"version": __version__,
		}
		self.write(status)

#-------------------------------------------------------------------------------

class RequestHandler(tornado.web.RequestHandler):

	"""Format of this string is host:port/database. It's used to construct
	a URL when talking to the key store."""
	key_store = None

	def _handle_key_store_get_response(self, response):
		if response.code == httplib.NOT_FOUND:
			self.set_status(httplib.NOT_FOUND)
			self.finish()
			return

		if response.code != httplib.OK:
			self.set_status(httplib.INTERNAL_SERVER_ERROR)
			self.finish()
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

		self.write(json.dumps(rv))
		self.set_header("Content-Type", "application/json; charset=utf8") 
		self.finish()

	@tornado.web.asynchronous
	def get(self, mac_key_identifier=None):
		if mac_key_identifier:
			url = "http://%s/%s" % (self.__class__.key_store, mac_key_identifier)
		else:
			owner = self.get_argument("owner", None)
			if owner:
				url = 'http://%s/_design/creds/_view/by_owner?startkey="%s"&endkey="%s"' % (
					self.__class__.key_store,
					owner,
					owner)
			else:
				url = "http://%s/_design/creds/_view/all" % self.__class__.key_store
				
		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(
			tornado.httpclient.HTTPRequest(
				url=url,
				method="GET",
				follow_redirects=False),
			callback=self._handle_key_store_get_response)

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

	def _handle_key_store_post_response(self, response):
		if response.code != httplib.CREATED:
			self.set_status(httplib.INTERNAL_SERVER_ERROR)
			self.finish()
			return

		location_url = "%s/%s" % (
			self.request.full_url(),
			response.request.headers["X-MAC-Key-Identifier"])
		self.set_header("Location", location_url)
		self.set_status(httplib.CREATED)
		self.finish()

	@tornado.web.asynchronous
	def post(self, mac_key_identifer=None):
		if mac_key_identifer is not None:
			self.set_status(httplib.METHOD_NOT_ALLOWED)
			return

		owner = self._get_owner_from_request_body()
		if owner is None:
			self.set_status(httplib.BAD_REQUEST)
			return

		creds = {
		   "owner": owner,
		   "mac_key_identifier": str(uuid.uuid4()).replace("-",""),
		   "mac_key": str(uuid.uuid4()).replace("-",""),
		   "mac_algorithm": "hmac-sha-1",
		   "type": "cred_v1.0",
		   "is_deleted": False,
		}
		headers = {
			"Content-Type": "application/json; charset=utf8",
			"Accept": "application/json",
			"Accept-Encoding": "charset=utf8",
			"X-MAC-Key-Identifier": creds["mac_key_identifier"],
		}
		url = "http://%s/%s" % (
			self.__class__.key_store,
			creds["mac_key_identifier"])
		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(
			tornado.httpclient.HTTPRequest(
				url,
				method="PUT",
				headers=tornado.httputil.HTTPHeaders(headers),
				body=json.dumps(creds)),
			callback=self._handle_key_store_post_response)

	def delete(self, mac_key_identifer=None):
		if mac_key_identifer is None:
			self.set_status(httplib.METHOD_NOT_ALLOWED)
			return

		creds = maccreds.MACcredentials.get(mac_key_identifer)
		if creds is None:
			self.clear()
			self.set_status(httplib.NOT_FOUND)
		else:
			if not creds.is_deleted:
				creds.delete()

#-------------------------------------------------------------------------------

_tornado_handlers = [
	(r"/status", StatusHandler),
	(r"/v1.0/mac_creds(?:/([^/]+))?", RequestHandler),
]

_tornado_app = tornado.web.Application(handlers=_tornado_handlers)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	clp = CommandLineParser()
	(clo, cla) = clp.parse_args()

	couchdb.couchdb_server = clo.key_store
	RequestHandler.key_store = clo.key_store

	http_server = tornado.httpserver.HTTPServer(_tornado_app)
	http_server.listen(clo.port)

	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
