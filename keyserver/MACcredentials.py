#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# MACcredentials.py
#	http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-00
#
# :TODO:
#	remove http://localhost:5984/macaa hard-coding
#
#-------------------------------------------------------------------------------

import json
import datetime
import uuid

import tornado.httpclient

class MACcredentials(object):

	_mac_algorithm = "hmac-sha-1"
	# section 5 of http://www.ietf.org/rfc/rfc0822.txt
	# example: Thu, 02 Dec 2010 21:39:45 GMT
	_rfc_822_sect_5_datetime_fmt_str = "%a, %d %b %Y %H:%M:%S GMT"

	@classmethod
	def _uuidstr(cls):
		return str(uuid.uuid4()).replace("-","")

	def __init__(self, owner, dict=None):
		object.__init__(self)

		if owner is not None:
			assert dict is None
			self.owner = owner
			self.mac_key_identifier = self.__class__._uuidstr()
			self.mac_key = self.__class__._uuidstr()
			self.mac_algorithm = self.__class__._mac_algorithm
			issue_time = datetime.datetime.utcnow()
			format_str = self.__class__._rfc_822_sect_5_datetime_fmt_str
			self.issue_time = issue_time.strftime(format_str)

			self.is_deleted = False
			self._rev = None
		else:
			assert dict is not None
			self.owner = dict["owner"]
			self.mac_key_identifier = dict["mac_key_identifier"]
			self.mac_key = dict["mac_key"]
			self.mac_algorithm = dict["mac_algorithm"]
			self.issue_time = dict["issue_time"]
			self.is_deleted = dict.get("is_deleted",False)
			self._rev = dict.get("_rev",None)

	@classmethod
	def get_all(cls,owner=None):
		http_client = tornado.httpclient.HTTPClient()
		# :TODO: this should not be hard-coded
		if owner is not None:
			url = "http://localhost:5984/macaa/_design/creds/_view/by_owner?startkey=\"%s\"&endkey=\"%s\"" % (owner, owner)
		else:
			url = "http://localhost:5984/macaa/_design/creds/_view/all"
		response = http_client.fetch(url)
		body = json.loads(response.body)
		rv = []
		for row in body['rows']:
			doc = row['value']
			creds = cls(None,doc)
			rv.append(creds)
		return rv

	@classmethod
	def get(cls,mac_key_dentifier):
		http_client = tornado.httpclient.HTTPClient()
		# :TODO: should not be hardcoded
		url = 'http://localhost:5984/macaa/%s' % mac_key_dentifier
		# :TODO: deal with id not being found
		response = http_client.fetch(url)
		if response is None:
			return None
		return cls(None,json.loads(response.body))

	def save(self):
		http_client = tornado.httpclient.HTTPClient()
		response = http_client.fetch(
			# :TODO: this should not be hard-coded
			"http://localhost:5984/macaa/%s" % self.mac_key_identifier,
			method='PUT',
			headers={"Content-Type": "application/json; charset=utf8"},
			body=json.dumps(self._asDict(True)))

	def delete(self):
		self.is_deleted = True
		http_client = tornado.httpclient.HTTPClient()
		response = http_client.fetch(
			# :TODO: this should not be hard-coded
			"http://localhost:5984/macaa/%s" % self.mac_key_identifier,
			method="PUT",
			headers={"Content-Type": "application/json; charset=utf8"},
			body=json.dumps(self._asDict(True))
			)

	def _asDict(self,is_for_couch=False):
		dict = {
			"owner": self.owner,
			"mac_key_identifier": self.mac_key_identifier,
			"mac_key": self.mac_key,
			"mac_algorithm": self.mac_algorithm,
			"issue_time": self.issue_time,
		}
		if self.is_deleted:
			dict["is_deleted"] = True
		if is_for_couch:
			dict["type"] = "cred",
			dict["_id"] = self.mac_key_identifier
			if self._rev is not None:
				dict["_rev"] = self._rev
		return dict

if __name__ == "__main__":
	pass

#------------------------------------------------------------------- End-of-File
