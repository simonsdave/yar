#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# maccreds_unit_tests.py
#
#-------------------------------------------------------------------------------

import unittest

import maccreds

class Test(unittest.TestCase):

	def test_ctr( self ):
		owner = "boo"
		mac_credentials = maccreds.MACcredentials( "boo" )
		self.assertTrue( mac_credentials.owner == owner )
		self.assertTrue( mac_credentials.mac_key_identifier is not None )
		self.assertTrue( mac_credentials.mac_key is not None )
		self.assertTrue( mac_credentials.mac_algorithm is not None )

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
