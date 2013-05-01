"""This module is used to generate the message authentication code (MAC)
used in HTTP MAC access authentication scheme. See [1] for details.

[1] http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-01"""

#-------------------------------------------------------------------------------

import logging
logging.basicConfig(level=logging.INFO)
import string
import random
import datetime
import hashlib
import hmac
import base64
import re

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

class Ext(object):
	"""Implements the notion of the ext as described in
	http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.1"""

	def __init__(self, content_type, body):
		object.__init__(self)

		if content_type and body: 
			hash_of_body = hashlib.new('sha1', body)
			hash_of_body = hash_of_body.digest()
			self._ext = "%s-%s" % (content_type, hash_of_body)
			self._ext = base64.b64encode(self._ext)
		else:
			self._ext = ""

	def __str__(self):
		return self._ext
			
#-------------------------------------------------------------------------------

class NormalizedRequestString(object):
	"""Implements the notion of a normalized request string as described in
	http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.2.1"""

	def __init__(self, ts, nonce, http_method, uri, host, port, ext):
		object.__init__(self)

		self.ts = ts
		self.nonce = nonce
		self.http_method = http_method
		self.uri = uri
		self.host = host
		self.port = port
		self.ext = ext

		self._normalized_request_string = str(ts) + '\n' + \
			str(self.nonce) + '\n' + \
			self.http_method + '\n' + \
			self.uri + '\n' + \
			self.host + '\n' + \
			str(self.port) + '\n' + \
			str(self.ext) + '\n'

	def __str__(self):
		return self._normalized_request_string
			
#-------------------------------------------------------------------------------

class MAC(object):
	"""Implements notion of a message authentication code according to
	http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02"""

	def __init__(self, mac_key, mac_algorithm, normalized_request_string):
		object.__init__(self)

		self.mac_key = mac_key
		self.mac_algorithm = mac_algorithm
		self.normalized_request_string = normalized_request_string

		self._mac_algorithm = \
			hashlib.sha256 if mac_algorithm == "hmac-sha-256" \
			else hashlib.sha1

		my_hmac = hmac.new(
			self.mac_key,
			str(self.normalized_request_string),
			self._mac_algorithm)
		self._base64_encoded_hmac = base64.b64encode(my_hmac.digest())

	def __str__(self):
		return self._base64_encoded_hmac
			
#-------------------------------------------------------------------------------

class AuthHeaderValue(object):
	"""As per http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02 create
	the value for the HTTP Authorization header using and an existing hmac."""

	def __init__(self, mac_key_identifier, ts, nonce, ext, mac):
		object.__init__(self)

		self.mac_key_identifier = mac_key_identifier
		self.ts = ts
		self.nonce = nonce
		self.ext = ext
		self.mac = mac

		fmt = 'MAC id="%s", ts="%s", nonce="%s", ext="%s", mac="%s"'
		self._value = fmt % (
			self.mac_key_identifier,
			self.ts,
			self.nonce,
			self.ext,
			self.mac) 

	def __str__(self):
		return self._value

	@classmethod
	def parse(cls, value):
		"""Given an authorization header value parse it and
		create an AuthHeaderValue. If ```value``` is None or
		in an unrecognized format return None."""
		if not value:
			return None
		
		reg_ex = re.compile(
			'^\s*MAC\s+id\s*\=\s*"(?P<mac_key_identifier>[^"]+)"\s*\,\s*ts\s*\=\s*"(?P<ts>[^"]+)"\s*\,\s*nonce\s*\=\s*"(?P<nonce>[^"]+)"\s*\,\s*ext\s*\=\s*"(?P<ext>[^"]*)"\s*\,\s*mac\s*\=\s*"(?P<mac>[^"]+)"\s*$',
			re.IGNORECASE)
		match = reg_ex.match(value)
		if not match:
			_logger.info(
				"Invalid format for authorization header '%s'",
				value)
			return False
		_logger.info(
			"Valid format for authorization header '%s'",
			value)

		assert 0 == match.start()
		assert len(value) == match.end()
		assert 5 == len(match.groups())

		mac_key_identifier = match.group("mac_key_identifier")
		assert mac_key_identifier
		assert 0 < len(mac_key_identifier)

		ts = match.group("ts")
		assert ts
		assert 0 < len(ts)

		nonce = match.group("nonce")
		assert nonce
		assert 0 < len(nonce)

		ext = match.group("ext")
		assert ext is not None
		assert 0 <= len(ext)

		mac = match.group("mac")
		assert mac
		assert 0 < len(mac)

		return cls(mac_key_identifier, ts, nonce, ext, mac)

#------------------------------------------------------------------- End-of-File
