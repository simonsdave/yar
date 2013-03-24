#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# keyserver.py
#
#-------------------------------------------------------------------------------

import httplib
import re
import json

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

import maccreds

#-------------------------------------------------------------------------------

define("port", default=8000, help="run on the given port", type=int)

#-------------------------------------------------------------------------------

class StatusHandler(tornado.web.RequestHandler):

	def get(self):
		status = {
			"status": "ok",
			"version": "1.0",
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
			self.set_status(httplib.BAD_REQUEST)
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

	def _get_request_body_as_dict_from_json(self):
		if not self._is_json_utf8_content_type():
			return None
		body = self.request.body
		if body is None:
			return None
		try:
			return json.loads(body)
		except:
			pass
		return None

	def get(self):
		owner = self.get_argument("owner",None)
		self.write_creds(maccreds.MACcredentials.get_all(owner))

	def post(self):
		body = self._get_request_body_as_dict_from_json()
		if body is None:
			self.set_status(httplib.BAD_REQUEST)
		else:
			creds = maccreds.MACcredentials(body["owner"])
			creds.save()
			self.set_header(
				"Location",
				"%s/%s" % (self.request.full_url(), creds.mac_key_identifier))

#-------------------------------------------------------------------------------

class ACredsHandler(CredsHandler):

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
			creds.delete()

#-------------------------------------------------------------------------------

_tornado_handlers = [
	(r"/status", StatusHandler),
	(r"/v1.0/mac_creds", AllCredsHandler),
	(r"/v1.0/mac_creds/([^/]+)", ACredsHandler)
]
_tornado_app = tornado.web.Application(handlers=_tornado_handlers)

if __name__ == "__main__":
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(_tornado_app)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
