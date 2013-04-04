#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# maccreds.py
#
#	See http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-00
#	for context on this module.
#
#-------------------------------------------------------------------------------

import json
import datetime
import uuid

from couchdb import CouchDB

#-------------------------------------------------------------------------------

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
		cdb = CouchDB()
		if owner is not None:
			response = cdb.get(
				"_design/creds/_view/by_owner?startkey=\"%s\"&endkey=\"%s\"",
				owner,
				owner)
		else:
			response = cdb.get("_design/creds/_view/all")
		body = json.loads(response.body)
		rv = []
		for row in body['rows']:
			doc = row['value']
			creds = cls(None,doc)
			rv.append(creds)
		return rv

	@classmethod
	def get(cls, mac_key_identifier):
		cdb = CouchDB()
		response = cdb.get(mac_key_identifier)
		if response is None:
			return None
		return cls(None,json.loads(response.body))

	def save(self):
		cdb = CouchDB()
		response = cdb.put(self._as_dict(), self.mac_key_identifier)

	def delete(self):
		self.is_deleted = True
		self.save()

	def _as_dict(self):
		dict = {
			"owner": self.owner,
			"mac_key_identifier": self.mac_key_identifier,
			"mac_key": self.mac_key,
			"mac_algorithm": self.mac_algorithm,
			"issue_time": self.issue_time,
			"type": "cred_v1.0",
			"_id": self.mac_key_identifier,
		}
		if self.is_deleted:
			dict["is_deleted"] = True
		if self._rev is not None:
			dict["_rev"] = self._rev
		return dict

if __name__ == "__main__":
	pass

#------------------------------------------------------------------- End-of-File
