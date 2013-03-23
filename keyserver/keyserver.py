#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# keyserver.py
#
#-------------------------------------------------------------------------------

import json

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

from MACcredentials import MACcredentials

define("port", default=8000, help="run on the given port", type=int)

class JSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, MACcredentials):
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

class CredsHandler(tornado.web.RequestHandler):

	def write_creds(self,creds):
		if creds is None:
			self.clear()
			self.set_status(404)
		else:
			self.write(json.dumps(creds,cls=JSONEncoder))
			self.set_header("Content-Type", "application/json; charset=utf8") 

class AllCredsHandler(CredsHandler):

	# curl -s -X GET http://localhost:6969/v1.0/mac_creds
	def get(self):
		owner = self.get_argument("owner",None)
		self.write_creds(MACcredentials.get_all(owner))

	# curl -X POST -H "Content-Type: application/json; charset=utf8" -d "{\"owner\":\"dave.simons@points.com\"}" http://localhost:6969/v1.0/mac_creds/
	def post(self):
		# :TODO: check content type
		body = json.loads(self.request.body)
		if 'owner' not in body:
			self.set_status(404)
			return
		owner = body['owner']
		
		creds = MACcredentials(owner)
		creds.save()

class ACredsHandler(CredsHandler):

	# curl -v -X GET http://localhost:6969/v1.0/mac_creds/b205c21fbc467b4d28aa93fba7000d12
	def get(self,mac_key_identifer):
		assert mac_key_identifer is not None
		self.write_creds(MACcredentials.get(mac_key_identifer))

	# curl -v -X DELETE http://localhost:6969/v1.0/mac_creds/b205c21fbc467b4d28aa93fba7000d12
	def delete(self,mac_key_identifer):
		assert mac_key_identifer is not None
		creds = MACcredentials.get(mac_key_identifer)
		if creds is None:
			self.clear()
			self.set_status(404)
		else:
			creds.delete()

if __name__ == "__main__":
	tornado.options.parse_command_line()
	handlers = [
		(r"/v1.0/mac_creds(?:/){0,1}", AllCredsHandler),
		(r"/v1.0/mac_creds/([^/]+)", ACredsHandler)
	]
	app = tornado.web.Application(handlers=handlers)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
