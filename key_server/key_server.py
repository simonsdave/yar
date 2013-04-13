#!/usr/bin/env python
"""This module contains the core key server logic."""

import httplib
import re
import json

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import couchdb
import maccreds

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

class MACCredsJSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, maccreds.MACcredentials):
			rv = {
				"owner": obj.owner,
				"mac_key_identifier": obj.mac_key_identifier,
				"mac_key": obj.mac_key,
				"mac_algorithm": obj.mac_algorithm,
				"issue_time": obj.issue_time,
			}
			if obj.is_deleted:
				rv["is_deleted"] = True
			return rv
		return json.JSONEncoder.default(self, obj)

#-------------------------------------------------------------------------------

class CredsHandler(tornado.web.RequestHandler):

	def write_creds(self,creds):
		if creds is None:
			self.clear()
			self.set_status(httplib.NOT_FOUND)
		else:
			self.write(json.dumps(creds,cls=MACCredsJSONEncoder))
			self.set_header("Content-Type", "application/json; charset=utf8") 

#-------------------------------------------------------------------------------

class AllCredsHandler(CredsHandler):

	_json_utf8_content_type_reg_ex = re.compile(
		"^\s*application/json;\s+charset\=utf-{0,1}8\s*$",
		re.IGNORECASE )

	def _is_json_utf8_content_type(self):
		content_type = self.request.headers.get("content-type", None)
		if content_type is None:
			return False
		if not self.__class__._json_utf8_content_type_reg_ex.match(content_type):
			return False
		return True

	def get(self):
		owner = self.get_argument("owner", None)
		self.write_creds(maccreds.MACcredentials.get_all(owner))

	def _get_owner_from_request_body(self):
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

	def post(self):
		owner = self._get_owner_from_request_body()
		if owner is None:
			self.set_status(httplib.BAD_REQUEST)
			return

		creds = maccreds.MACcredentials(owner)
		creds.save()
		location_url = "%s/%s" % (
			self.request.full_url(),
			creds.mac_key_identifier)
		self.set_header("Location", location_url)
		self.set_status(httplib.CREATED)

#-------------------------------------------------------------------------------

class CredsHandler(CredsHandler):

	def get(self,mac_key_identifer):
		assert mac_key_identifer is not None
		self.write_creds(maccreds.MACcredentials.get(mac_key_identifer))

	def delete(self,mac_key_identifer):
		assert mac_key_identifer is not None
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
	(r"/v1.0/mac_creds", AllCredsHandler),
	(r"/v1.0/mac_creds/([^/]+)", CredsHandler),
]

_tornado_app = tornado.web.Application(handlers=_tornado_handlers)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	tornado.options.define(
		"port",
		default=8070,
		help="run on the given port",
		type=int)
	tornado.options.define(
		"key_store",
		default="localhost:5984/macaa",
		help="<host>:<port>/<database> - default = localhost:5984/macaa",
		type=str)
	tornado.options.parse_command_line()
	couchdb.couchdb_server = tornado.options.options.key_store

	http_server = tornado.httpserver.HTTPServer(_tornado_app)
	http_server.listen(tornado.options.options.port)

	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
