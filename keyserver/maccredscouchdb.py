#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# maccredscouchdb.py
#
#-------------------------------------------------------------------------------

import httplib

import couchdb

#-------------------------------------------------------------------------------

class CouchDB(couchdb.CouchDB):

	def get_all_for_owner(self, owner=None):
		if owner is None:
			(http_status_code,rv) = self.get("_design/creds/_view/all")
			if httplib.OK != http_status_code:
				return None
			return rv
		(http_status_code,rv) = cdb.get(
			"_design/creds/_view/by_owner?startkey=\"%s\"&endkey=\"%s\"",
			owner,
			owner)
		if httplib.OK != http_status_code:
			return None
		return rv

	def get_for_mac_key_identifier(self, mac_key_identifier):
		(http_status_code,rv) = self.get(mac_key_identifier)
		if httplib.OK != http_status_code:
			return None
		return rv

	def save(self, mac_key_identifier, maccreds):
		(http_status_code,ignore) = self.put(
   			maccreds,
			mac_key_identifier)
		return httplib.OK == http_status_code

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	pass

#------------------------------------------------------------------- End-of-File
