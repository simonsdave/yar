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
		if 'owner' not in body:
			self.set_status(404)
			return
		mac_creds = MACcredentials.MACcredentials( body['owner'] )
		body = json.dumps(mac_creds,cls=JSONEncoder)
		http_client = tornado.httpclient.HTTPClient()
		response = http_client.fetch(
			"http://localhost:5984/macaa/",		# :TODO: this should not be hard-coded
			method='POST',
			headers={"Content-Type": "application/json; charset=utf8"},
			body=body )

class CredsHandler(tornado.web.RequestHandler):

	# curl -v -X GET http://localhost:6969/mac_creds/b205c21fbc467b4d28aa93fba7000d12
	def get(self,id):
		value = self._get(id)
		if value is None:
			self.clear()
			self.set_status(404)
		else:
			# since value is a dict self.write() will correctly set the content type
			self.write(value)

	# curl -v -X DELETE http://localhost:6969/mac_creds/b205c21fbc467b4d28aa93fba7000d12
	def delete(self,id):
		doc = self._get(id)
		if doc is None:
			self.clear()
			self.set_status(404)
		else:
			doc["is_deleted"] = True
			http_client = tornado.httpclient.HTTPClient()
			response = http_client.fetch(
				"http://localhost:5984/macaa/%s" % id,	# :TODO: should not be hardcoded
				method="PUT",
				headers={"Content-Type": "application/json; charset=utf8"},
				body=json.dumps(doc)
				)

	def _get(self,id):
		http_client = tornado.httpclient.HTTPClient()
		# :TODO: should not be hardcoded
		url = 'http://localhost:5984/macaa/%s' % id
		# :TODO: deal with id not being found
		response = http_client.fetch(url)
		if response is None:
			return None
		return json.loads(response.body)

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
