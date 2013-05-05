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
import base64

import mac

#-------------------------------------------------------------------------------

class NonceTestCase(unittest.TestCase):
	
	def test_compute_returns_non_none_Nonces(self):
		for i in range(0,1024):
			nonce = mac.Nonce.compute()
			self.assertIsNotNone(nonce)
			self.assertEqual(nonce.__class__, mac.Nonce)
			self.assertTrue(8 <= len(nonce))
			self.assertTrue(len(nonce) <= 16)
			for i in range(0,len(nonce)):
				self.assertTrue(nonce[i] in (string.ascii_lowercase + string.digits))

	def test_created_with_explicit_content(self):
		content = 'dave was here'
		nonce = mac.Nonce(content)
		self.assertIsNotNone(nonce)
		self.assertEqual(nonce, content)

#-------------------------------------------------------------------------------

class TimestampTestCase(unittest.TestCase):
	
	def test_compute_returns_non_none_Timestamp_which_represents_integer(self):
		ts = mac.Timestamp.compute()
		self.assertIsNotNone(ts)
		self.assertEqual(ts.__class__, mac.Timestamp)
		self.assertTrue(0 < len(ts))
		self.assertEqual(int, int(ts).__class__)

	def test_created_with_explicit_content(self):
		content = '45'
		ts = mac.Timestamp(content)
		self.assertIsNotNone(ts)
		self.assertEqual(ts, content)

#-------------------------------------------------------------------------------

class ExtTestCase(unittest.TestCase):
	
	def test_content_type_and_body_none_is_zero_length_ext(self):
		content_type = None
		body = None
		ext = mac.Ext.compute(content_type, body)
		self.assertIsNotNone(ext)
		self.assertEqual(ext, "")

	def test_content_type_not_none_and_body_none_is_zero_length_ext(self):
		content_type = "dave was here"
		body = None
		ext = mac.Ext.compute(content_type, body)
		self.assertIsNotNone(ext)
		self.assertEqual(ext, "")

	def test_content_type_none_and_body_not_none_is_zero_length_ext(self):
		content_type = None
		body = "dave was here"
		ext = mac.Ext.compute(content_type, body)
		self.assertIsNotNone(ext)
		self.assertEqual(ext, "")

	def test_content_type_and_body_not_none_is_sha1_of_both(self):
		content_type = "hello world!"
		body = "dave was here"
		ext = mac.Ext.compute(content_type, body)
		self.assertIsNotNone(ext)
		hash = hashlib.new('sha1', content_type + body)
		self.assertEqual(ext, hash.hexdigest())

	def test_created_with_explicit_content(self):
		content = "abc"
		ext = mac.Ext(content)
		self.assertIsNotNone(ext)
		self.assertEqual(content, ext)

#-------------------------------------------------------------------------------

class MACTestCase(unittest.TestCase):

	def _uuid(self):
		return str(uuid.uuid4()).replace("-","")
	
#-------------------------------------------------------------------------------

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
