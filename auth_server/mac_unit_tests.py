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

import mac

#-------------------------------------------------------------------------------

class NonceTestCase(unittest.TestCase):
	
	def test_it(self):
		nonce = mac.Nonce()
		self.assertTrue(8 <= len(nonce))
		self.assertTrue(len(nonce) <= 16)
		for i in range(0,len(nonce)):
			self.assertTrue(nonce[i] in (string.ascii_lowercase + string.digits))
		print nonce

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
