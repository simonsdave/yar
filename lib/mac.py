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

	The implementation for this class was strongly influenced by [1].

	[1] http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits."""

	def __new__(self, nonce):
		return str.__new__(self, nonce)

	@classmethod
	def compute(cls):
		chars = string.ascii_lowercase + string.digits
		r = random.Random()
		nonce_len = 8 + r.randint(0,8)
		nonce = ''.join(random.choice(chars) for i in range(nonce_len))
		return cls(nonce)

#-------------------------------------------------------------------------------

class Timestamp(str):
	"""Represents the # of seconds since 1st Jan 1970."""

	def __new__(self, ts):
		return str.__new__(self, ts)

	@classmethod
	def compute(cls):
		epoch = datetime.datetime(1970, 1, 1, 0, 0, 0)
		ts = int((datetime.datetime.utcnow() - epoch).total_seconds())
		return cls(ts)
		
#-------------------------------------------------------------------------------

class Ext(str):
	"""Implements the notion of the ext as described in
	http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.1"""

	def __new__(self, ext):
		return str.__new__(self, ext)

	@classmethod
	def compute(cls, content_type, body):

		if content_type is not None and body is not None: 
			content_type_plus_body = content_type + body
			content_type_plus_body_hash = hashlib.sha1(content_type_plus_body)
			ext = content_type_plus_body_hash.hexdigest()
		else:
			ext = ""

		return cls(ext)

#-------------------------------------------------------------------------------

class NormalizedRequestString(str):
	"""Implements the notion of a normalized request string as described in
	http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.2.1"""

	def __new__(self, normalized_request_string):
		return str.__new__(self, normalized_request_string)

	@classmethod
	def compute(cls, ts, nonce, http_method, uri, host, port, ext):
		normalized_request_string = \
			ts + '\n' + \
			nonce + '\n' + \
			http_method + '\n' + \
			uri + '\n' + \
			host + '\n' + \
			str(port) + '\n' + \
			ext + '\n'
		return cls(normalized_request_string)

#-------------------------------------------------------------------------------

class MAC(str):
	"""Implements concept of a message authentication code according to
	http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02"""

	def __new__(self, mac):
		return str.__new__(self, mac)

	@classmethod
	def compute(cls, mac_key, mac_algorithm, normalized_request_string):
		"""Compute a request's MAC given a normalized request sring (aka
		a summary of the key elements of the request, the mac key and
		the algorithm."""

		# :TODO: the str() on the mac key below seems required because of
        # a bug introducted in python 2.6 as per http://bugs.python.org/issue5285
		dm = hashlib.sha256 if mac_algorithm == "hmac-sha-256" else hashlib.sha1
		mac = hmac.new(str(mac_key), normalized_request_string, dm)
		return cls(mac.hexdigest())

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
		ts = Timestamp(ts)

		nonce = match.group("nonce")
		assert nonce
		assert 0 < len(nonce)
		nonce = Nonce(nonce)

		ext = match.group("ext")
		assert ext is not None
		assert 0 <= len(ext)
		ext = Ext(ext)

		mac = match.group("mac")
		assert mac
		assert 0 < len(mac)
		mac = MAC(mac)

		return cls(mac_key_identifier, ts, nonce, ext, mac)

#------------------------------------------------------------------- End-of-File
