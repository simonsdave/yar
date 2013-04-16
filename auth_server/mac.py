#!/usr/bin/env python
"""This module is used to generate the message authentication code (MAC)
used in HTTP MAC access authentication scheme. See [1] for details.

[1] http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-01"""

#-------------------------------------------------------------------------------

import logging
logging.basicConfig(level=logging.FATAL)
import string
import random
import datetime
import hashlib
import hmac
import base64

#-------------------------------------------------------------------------------

_logger = logging.getLogger("MAC%s" % __name__)

#-------------------------------------------------------------------------------

__version__ = "1.0"

#-------------------------------------------------------------------------------

class Nonce(str):
	"""This class generates an N character random string where the characters
	are selected from both all the lower case letters and numbers 0 to 9 and N
	is between 8 and 16. The resulting string is intendend to be used
	as the nonce in MAC access authenciation.

	The implementation for this method was strongly influenced by [1].

	[1] http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits."""

	def __new__(self):
		""""""
		chars = string.ascii_lowercase + string.digits
		r = random.Random()
		nonce_len = 8 + r.randint(0,8)
		rstr = ''.join(random.choice(chars) for i in range(nonce_len))
		return str.__new__(self, rstr)

#-------------------------------------------------------------------------------

class Timestamp(object):
	"""..."""

	def __init__(self):
		epoch = datetime.datetime(1970, 1, 1, 0, 0, 0)
		self._ts = int((datetime.datetime.utcnow() - epoch).total_seconds())

	def __str__(self):
		return str(self._ts)

#-------------------------------------------------------------------------------

class Mac(object):
	"""..."""

	def __init__(
		self,
		mac_key,
		mac_algorithm,
		ts,
		nonce,
		http_method,
		uri,
		host,
		port,
		content_type = None,
		md5_of_body = None):

		assert mac_algorithm == "hmac-sha-1" or mac_algorithm == "hmac-sha-256"

		if mac_algorithm == "hmac-sha-1":
			self._mac_algorithm = hashlib.sha1
		else:
			self._mac_algorithm = hashlib.sha256

		assert (content_type is None and md5_of_body is None) or \
			   (content_type is not None and md5_of_body is not None)

		if content_type is None:
			self._ext = ""
		else:
			self._ext = "%s-%s" % (content_type, md5_of_body or "")

		self._normalized_request_string = str(ts) + '\n' + \
			str(nonce) + '\n' + \
			http_method + '\n' + \
			uri + '\n' + \
			host + '\n' + \
			str(port) + '\n' + \
			self._ext + '\n'

		self._hmac = hmac.new(
			mac_key,
			self._normalized_request_string,
			self._mac_algorithm)
		self._base64_encoded_hmac = base64.b64encode( self._hmac.digest() )

	def __str__(self):
		return self._base64_encoded_hmac
			
#------------------------------------------------------------------- End-of-File
