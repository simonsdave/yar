#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# couchdb.py
#
#-------------------------------------------------------------------------------

import json

import tornado.httpclient

#-------------------------------------------------------------------------------

class CouchDB(object):

	_host = "localhost"
	_port = "5984"
	_database = "macaa"

	def _url(self,path,*args):
		url = "http://%s:%s/%s/%s" % (
			self.__class__._host,
			self.__class__._port,
			self.__class__._database,
			# :TODO: is the args[0][0] below really the right way to do this?
			(path % args[0][0])
			)
		return url

	def _fetch(self,dict,path,*args):
		url = self._url(path,args)
		http_client = tornado.httpclient.HTTPClient()
		if dict is None:
			response = http_client.fetch(url)
		else:
			response = http_client.fetch(
				url,
				method='PUT',
				headers={"Content-Type": "application/json; charset=utf8"},
				body=json.dumps(dict))
		return response

	def get(self,path,*args):
		return self._fetch(None,path,args)

	def put(self,dict,path,*args):
		return self._fetch(dict,path,args)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	pass

#------------------------------------------------------------------- End-of-File
