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

define("port", default=8000, help="run on the given port", type=int)

class JSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, MACcredentials.MACcredentials):
			rv = {
				"owner": obj.owner,
				"mac_key_identifier": obj.mac_key_identifier,
				"mac_key": obj.mac_key,
				"mac_algorithm": obj.mac_algorithm,
				"issue_time": obj.issue_time,
				# :TODO: is this the right place for 'type' to get added?
				"type": "cred",
			}
			return rv
		return json.JSONEncoder.default(self, obj)

class AllCredsHandler(tornado.web.RequestHandler):

	# curl -s -X GET http://localhost:6969/mac_creds/
	# curl -s -X GET http://localhost:6969/mac_creds
	def get(self):
		http_client = tornado.httpclient.HTTPClient()
		# :TODO: this should not be hard-coded
		url = "http://localhost:5984/macaa/_design/creds/_view/all"
		response = http_client.fetch(url)
		body = json.loads(response.body)
		rows = []
		for row in body['rows']:
			rows.append( row['value'] )
		# what to do with the extra attributes that are leaking out?
		self.write(json.dumps(rows))
		self.set_header("Content-Type", "application/json; charset=utf8") 

	# curl -X POST -H "Content-Type: application/json; charset=utf8" -d "{\"owner\":\"dave.simons@points.com\"}" http://localhost:6969/mac_creds/
	def post(self):
		# :TODO: check content type
		body = json.loads(self.request.body)
		# :TODO: what if 'owner' not there?
		owner = body['owner']
		mac_creds = MACcredentials.MACcredentials( owner )
		# :TODO: need to ensure UTF8 encoding
		body = json.dumps(mac_creds,cls=JSONEncoder)
		# :TODO: this should not be hard-coded
		url = "http://localhost:5984/macaa/"
		headers = {"Content-Type": "application/json; charset=utf8"}
		http_client = tornado.httpclient.HTTPClient()
		response = http_client.fetch(
			url,
			method='POST',
			headers=headers,
			body=body
			)
		print 30*'-'
		print response
		print 30*'-'
		# self.write(">>>%s<<<" % json.dumps(body))

class CredsHandler(tornado.web.RequestHandler):
	def get(self,id):
		http_client = tornado.httpclient.HTTPClient()
		# :TODO: should not be hardcoded
		url_fmt = 'http://localhost:5984/macaa/_design/creds/_view/all?startkey="%s"&endkey="%s"'
		url = url_fmt % (id, id)
		response = http_client.fetch(url)
		body = json.loads(response.body)
		rows = body['rows']
		if 0 == len(rows):
			self.clear()
			self.set_status(404)
		else:
			row = rows[0]
			value = row['value']
			self.write(json.dumps(value))

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
