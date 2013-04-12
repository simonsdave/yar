#!/usr/bin/env python
"""This module contains a super simple app server to be used for testing."""

import datetime

import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.options
import tornado.web

#-------------------------------------------------------------------------------

class RequestHandler(tornado.web.RequestHandler):
	def get(self):
		dict = {
			"status": "ok",
			"version": "1.0",
			"when": str(datetime.datetime.now())
		}
		self.write(dict)

	def post(self):
		self.get()

	def put(self):
		self.get()

	def delete(self):
		self.get()

#-------------------------------------------------------------------------------

if __name__ == "__main__":

	tornado.options.define(
		"port",
		default=8080,
		help="run on this port - default = 8080",
		type=int)
	tornado.options.parse_command_line()

	app = tornado.web.Application(handlers=[(r".*", RequestHandler)])
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(tornado.options.options.port)
	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
