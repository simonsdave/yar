#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# maccreds.py
#
#	See http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-00
#	for context on this module.
#
#-------------------------------------------------------------------------------

import datetime
import uuid
import httplib

from maccredscouchdb import CouchDB

#-------------------------------------------------------------------------------

class MACcredentials(object):

	@classmethod
	def _uuidstr(cls):
		return str(uuid.uuid4()).replace("-","")

	def __init__(self, owner, dict=None):
		object.__init__(self)

		if owner is not None:
			self.owner = owner
			self.mac_key_identifier = self.__class__._uuidstr()
			self.mac_key = self.__class__._uuidstr()
			self.mac_algorithm = "hmac-sha-1"
			self.is_deleted = False
			self._rev = None
		else:
			self.owner = dict["owner"]
			self.mac_key_identifier = dict["mac_key_identifier"]
			self.mac_key = dict["mac_key"]
			self.mac_algorithm = dict["mac_algorithm"]
			self.is_deleted = dict.get("is_deleted",False)
			self._rev = dict.get("_rev",None)

	@classmethod
	def get_all(cls,owner=None):
		cdb = CouchDB()
		return cdb.get_all_for_owner(owner)

	@classmethod
	def get(cls, mac_key_identifier):
		cdb = CouchDB()
		dict = cdb.get_for_mac_key_identifier(mac_key_identifier)
		if dict is None:
			return None
		return cls(None,dict)

	def save(self):
		cdb = CouchDB()
		return cdb.save(self.mac_key_identifier,self._as_dict())

	def delete(self):
		self.is_deleted = True
		self.save()

	def _as_dict(self):
		dict = {
			"owner": self.owner,
			"mac_key_identifier": self.mac_key_identifier,
			"mac_key": self.mac_key,
			"mac_algorithm": self.mac_algorithm,
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
