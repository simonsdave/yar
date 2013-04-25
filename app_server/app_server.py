#!/usr/bin/env python
"""This module contains a super simple app server to be used for testing."""

import logging
import os
import sys
import datetime
import uuid
import httplib

import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web

from clparser import CommandLineParser

#-------------------------------------------------------------------------------

__version__ = "1.0"

#-------------------------------------------------------------------------------

_logger = logging.getLogger("APPSERVER_%s" % __name__)

#-------------------------------------------------------------------------------

class RequestHandler(tornado.web.RequestHandler):
	def get(self):
		dict = {
			"status": "ok",
			"version": __version__,
			"when": str(datetime.datetime.now())
		}
		self.write(dict)

	def post(self):
		location_url = "%s/%s" % (
			self.request.full_url(),
			str(uuid.uuid4()).replace("-",""))
		self.set_header("Location", location_url)
		self.set_status(httplib.CREATED)

	def put(self):
		self.get()

	def delete(self):
		self.get()

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	clp = CommandLineParser()
	(clo, cla) = clp.parse_args()

	logging.basicConfig(level=clo.logging_level)

	_logger.info(
		"%s %s running on %d",
		os.path.basename(os.path.split(sys.argv[0])[1]),
		__version__,
		clo.port)
		
	app = tornado.web.Application(handlers=[(r".*", RequestHandler)])
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(clo.port)
	tornado.ioloop.IOLoop.instance().start()

#------------------------------------------------------------------- End-of-File
