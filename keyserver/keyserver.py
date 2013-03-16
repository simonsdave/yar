#!/usr/bin/env python

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class AllCredsHandler(tornado.web.RequestHandler):
	def get(self):
		self.write(">>>all creds<<<")

class CredsHandler(tornado.web.RequestHandler):
	def get(self,key):
		self.write(">>>%s<<<" % key)

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
