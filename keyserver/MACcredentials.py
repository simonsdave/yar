#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# MACcredentials.py
#
#-------------------------------------------------------------------------------

import datetime
import uuid

# http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-00

class MACcredentials(object):

	_mac_algorithm = "hmac-sha-1"
	# section 5 of http://www.ietf.org/rfc/rfc0822.txt
	# example: Thu, 02 Dec 2010 21:39:45 GMT
	_rfc_822_sect_5_datetime_fmt_str = "%a, %d %b %Y %H:%M:%S GMT"

	@classmethod
	def _uuidstr(cls):
		return str(uuid.uuid4()).replace("-","")

	def __init__(self, owner):
		object.__init__(self)

		self.owner = owner
		self.mac_key_identifier = self.__class__._uuidstr()
		self.mac_key = self.__class__._uuidstr()
		self.mac_algorithm = self.__class__._mac_algorithm
		issue_time = datetime.datetime.utcnow()
		format_str = self.__class__._rfc_822_sect_5_datetime_fmt_str
		self.issue_time = issue_time.strftime(format_str)

	def __str__(self):
		return "%s/%s/%s/%s/%s" % (
			self.owner,
			self.mac_key_identifier,
			self.mac_key,
			self.mac_algorithm,
			self.issue_time
			)

	def asDict(self):
		dict = {
			"owner": self.owner,
			"mac_key_identifier": self.mac_key_identifier,
			"mac_key": self.mac_key,
			"mac_algorithm": self.mac_algorithm,
			"issue_time": self.issue_time
		}
		return dict

if __name__ == "__main__":
	pass

#------------------------------------------------------------------- End-of-File
