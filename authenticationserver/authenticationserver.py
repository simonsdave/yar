#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# authenticationserver.py
#
# key influences for this module
#	https://groups.google.com/forum/?fromgroups=#!msg/python-tornado/TB_6oKBmdlA/Js9JoOcI6nsJ
#
#-------------------------------------------------------------------------------

import re
import httplib

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

	# Authorization: MAC id="h480djs93hd8",
	#			         nonce="264095:dj83hs9s",
	#			         mac="SLDJd4mg43cjQfElUs3Qub4L6xE="
	_authorization_reg_ex = re.compile(
		'^\s*MAC\s+id\s*\=\s*"(?P<id>[^"]+)"\s*\,\s+nonce\s*\=\s*"(?P<nonce>[^"]+)"\s*\,\s+mac\s*\=\s*"(?P<mac>[^"]+)"\s*$',
		# '^\s*MAC\s+id\s*\=\s*"(?P<id>[^"]+)"\s*\,\s+nonce\s*\=\s*"(?P<nonce>[^"]+)"\s*\,\s+mac\s*\=\s*"(?P<mac>[^"]+)"\s*$',
		re.IGNORECASE )

	def _get_authorization_header_value(self):
		authorization_header_value = self.request.headers.get("Authorization", None)
		if authorization_header_value is None:
			return (None,None,None)
		
		print ">>>%s<<<" % authorization_header_value
		authorization_match = self.__class__._authorization_reg_ex.match(authorization_header_value)
		if not authorization_match:
			print "poo"
			return (None,None,None)

		print "dave"
		assert 0 == authorization_match.start()
		assert len(self.authorization_header_value) == authorization_match.end()
		assert 3 == len(authorization_match.groups())
		id = authorization_match.group( "id" )
		nonce = authorization_match.group( "nonce" )
		mac = authorization_match.group( "mac" )
		return (id,nonce,mac)

	@property
	def _forward_to(self):
		return tornado.options.options.forwardto

	@property
	def _pass_thru_headers(self):
		return tornado.options.options.passthruheaders

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
		(id, nonce, mac) = self._get_authorization_header_value()
		if id is None or nonce is None or mac is None:
			self.set_status(httplib.UNAUTHORIZED)
			self.finish()
			return
		print ">>>%s<<<>>>%s<<<>>>%s<<<" % (id, nonce, mac)

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
		default=["Date","Cache-Control","Content-Type","Location","Etag"],
		help="comma sep list of HTTP headers to pass thru proxy",
		multiple=True,
		type=str)
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(_tornado_app)
	http_server.listen(tornado.options.options.port)
	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
