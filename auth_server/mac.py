#!/usr/bin/env python
"""This module is used to generate the message authentication code (MAC)
used in HTTP MAC access authentication scheme. See [1] for details.

[1] http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-01"""

#-------------------------------------------------------------------------------

import logging
logging.basicConfig(level=logging.FATAL)
import string
import random

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

#------------------------------------------------------------------- End-of-File
