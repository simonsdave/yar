#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# mac_unit_tests.py
#
#-------------------------------------------------------------------------------

import logging
logging.basicConfig(level=logging.FATAL)
import unittest
import string
import time
import uuid
import hashlib

import mac

#-------------------------------------------------------------------------------

class NonceTestCase(unittest.TestCase):
	
	def test_it(self):
		for i in range(0,1024):
			nonce = mac.Nonce()
			self.assertTrue(8 <= len(nonce))
			self.assertTrue(len(nonce) <= 16)
			for i in range(0,len(nonce)):
				self.assertTrue(nonce[i] in (string.ascii_lowercase + string.digits))

#-------------------------------------------------------------------------------

class TimestampTestCase(unittest.TestCase):
	
	def test_it(self):
		ts1 = mac.Timestamp()

#-------------------------------------------------------------------------------

class MACTestCase(unittest.TestCase):

	def _uuid(self):
		return str(uuid.uuid4()).replace("-","")
	
#-------------------------------------------------------------------------------

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
