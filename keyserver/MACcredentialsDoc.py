#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# MACcredentialsDoc.py
#
#-------------------------------------------------------------------------------

import json

import tornado.httpclient
# import tornado.httputil

class MACcredentialsDoc(dict):

	@classmethod
	def get_all(cls,owner=None):
		http_client = tornado.httpclient.HTTPClient()
		# :TODO: this should not be hard-coded
		url = "http://localhost:5984/macaa/_design/creds/_view/all"
		response = http_client.fetch(url)
		body = json.loads(response.body)
		docs = []
		for row in body['rows']:
			doc = cls(row['value'])
			docs.append(doc)
		# what to do with the extra attributes that are leaking out?
		return docs

	@classmethod
	def get(cls,id):
		http_client = tornado.httpclient.HTTPClient()
		# :TODO: should not be hardcoded
		url = 'http://localhost:5984/macaa/%s' % id
		# :TODO: deal with id not being found
		response = http_client.fetch(url)
		if response is None:
			return None
		return cls(json.loads(response.body))

	def save(self):
		self._prep_for_couch()
		http_client = tornado.httpclient.HTTPClient()
		response = http_client.fetch(
			"http://localhost:5984/macaa/",		# :TODO: this should not be hard-coded
			method='POST',
			headers={"Content-Type": "application/json; charset=utf8"},
			body=json.dumps(self))

	def delete(self):
		self._prep_for_couch()
		self["is_deleted"] = True
		http_client = tornado.httpclient.HTTPClient()
		response = http_client.fetch(
			"http://localhost:5984/macaa/%s" % self["_id"],	# :TODO: should not be hardcoded
			method="PUT",
			headers={"Content-Type": "application/json; charset=utf8"},
			body=json.dumps(self)
			)

	def _prep_for_couch(self):
		self["type"] = "cred"

if __name__ == "__main__":
	pass

#------------------------------------------------------------------- End-of-File
