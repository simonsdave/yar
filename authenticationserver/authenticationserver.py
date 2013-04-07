#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# authenticationserver.py
#
# key influences for this module
#	https://groups.google.com/forum/?fromgroups=#!msg/python-tornado/TB_6oKBmdlA/Js9JoOcI6nsJ
#
#-------------------------------------------------------------------------------

import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.options
import tornado.web

#-------------------------------------------------------------------------------

class StatusHandler(tornado.web.RequestHandler):

	def get(self):
		status = {
			"status": "ok",
			"version": "1.0",
		}
		self.write(status)

#-------------------------------------------------------------------------------

class RequestHandler(tornado.web.RequestHandler):
	_headers_to_return=(
		"Date",
		"Cache-Control",
		"Content-Type",
		"Location",
		"Etag",
		)

	def initialize(self):
		tornado.web.RequestHandler.initialize(self)
		self._forward_to = tornado.options.options.forwardto
		self._pass_thru_headers = tornado.options.options.passthruheaders.split(",")

	def _handle_response(self, response):
		self.set_status(response.code) 
		for header in self._pass_thru_headers:
			if header in response.headers:
				self.set_header(header, response.headers.get(header)) 
		if response.body: 
			self.write(response.body) 
		self.finish()

	@tornado.web.asynchronous
	def _handle_request(self):
		http_client = tornado.httpclient.AsyncHTTPClient()
		http_client.fetch(
			tornado.httpclient.HTTPRequest( 
				url="http://%s%s" % (self._forward_to, self.request.uri),
				method=self.request.method, 
				body=(self.request.body or None), 
				headers=self.request.headers, 
				follow_redirects=False),
			callback=self._handle_response)

	def post(self):
		self._handle_request()

	def get(self):
		self._handle_request()

	def put(self):
		self._handle_request()

	def delete(self):
		self._handle_request()

#-------------------------------------------------------------------------------

# _tornado_handlers simplifies the _tornado_app constructor
_tornado_handlers=[
	(r"/status", StatusHandler),
	(r".*", RequestHandler),
	]
# _tornado_app simplifies construction of testing infrastructure
_tornado_app = tornado.web.Application(handlers=_tornado_handlers)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	tornado.options.define(
		"port",
		default=8000,
		help="run on this port",
		type=int)
	tornado.options.define(
		"forwardto",
		default="localhost:8080",
		help="after authentication forward requests to this host:port",
		type=str)
	tornado.options.define(
		"passthruheaders",
		default="Date,Cache-Control,Content-Type,Location,Etag",
		help="comma sep list of HTTP headers to pass thru proxy",
		type=str)
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(_tornado_app)
	http_server.listen(tornado.options.options.port)
	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
