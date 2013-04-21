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

	def save(self, mac_key_identifier, maccreds):
		(http_status_code,ignore) = self.put(
   			maccreds,
			mac_key_identifier)
		return httplib.OK == http_status_code

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	pass

#------------------------------------------------------------------- End-of-File
