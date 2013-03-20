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
import tornado.httpclient
import tornado.httputil
from tornado.options import define, options

import MACcredentials
from MACcredentialsDoc import MACcredentialsDoc

define("port", default=8000, help="run on the given port", type=int)

class AllCredsHandler(tornado.web.RequestHandler):

	# curl -s -X GET http://localhost:6969/mac_creds/
	# curl -s -X GET http://localhost:6969/mac_creds
	def get(self):
		docs = MACcredentialsDoc.get_all()
		self.write(json.dumps(docs))
		self.set_header("Content-Type", "application/json; charset=utf8") 

	# curl -X POST -H "Content-Type: application/json; charset=utf8" -d "{\"owner\":\"dave.simons@points.com\"}" http://localhost:6969/mac_creds/
	def post(self):
		# :TODO: check content type
		body = json.loads(self.request.body)
		if 'owner' not in body:
			self.set_status(404)
			return
		owner = body['owner']
		mac_creds = MACcredentials.MACcredentials(owner)
		doc = MACcredentialsDoc(mac_creds.asDict())
		doc.save()

class CredsHandler(tornado.web.RequestHandler):

	# curl -v -X GET http://localhost:6969/mac_creds/b205c21fbc467b4d28aa93fba7000d12
	def get(self,id):
		assert id is not None
		doc = MACcredentialsDoc.get(id)
		if doc is None:
			self.clear()
			self.set_status(404)
		else:
			# since value is a dict self.write() will correctly set the content type
			self.write(doc)

	# curl -v -X DELETE http://localhost:6969/mac_creds/b205c21fbc467b4d28aa93fba7000d12
	def delete(self,id):
		doc = MACcredentialsDoc.get(id)
		if doc is None:
			self.clear()
			self.set_status(404)
		else:
			doc.delete()

if __name__ == "__main__":
	tornado.options.parse_command_line()
	handlers = [
		(r"/mac_creds(?:/){0,1}", AllCredsHandler),
		(r"/mac_creds/([^/]+)", CredsHandler)
	]
	app = tornado.web.Application(handlers=handlers)
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
