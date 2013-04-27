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

class MacTestCase(unittest.TestCase):
	
	def test_sha1_mac_algorithm_string_ok(self):
		x = mac.Mac(
			"dave",
			"hmac-sha-1",
			mac.Timestamp(),
			mac.Nonce(),
			"GET",
			"/dave.html",
			"simonsfamily.ca",
			80)
		self.assertTrue(hashlib.sha1 == x._mac_algorithm)

	def test_sha256_mac_algorithm_string_ok(self):
		x = mac.Mac(
			"dave",
			"hmac-sha-256",
			mac.Timestamp(),
			mac.Nonce(),
			"GET",
			"/dave.html",
			"simonsfamily.ca",
			80)
		self.assertTrue(hashlib.sha256 == x._mac_algorithm)

	def test_invalid_mac_algorithm(self):
		with self.assertRaises(AssertionError):
			x = mac.Mac(
				"dave",
				"hmac-sha-whatever",
				mac.Timestamp(),
				mac.Nonce(),
				"GET",
				"/dave.html",
				"simonsfamily.ca",
				80)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
