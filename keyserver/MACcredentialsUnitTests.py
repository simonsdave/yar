#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# MACcredentialsUnitTests.py
#
#-------------------------------------------------------------------------------

import unittest

import MACcredentials

class Test(unittest.TestCase):

	def test_ctr( self ):
		owner = "boo"
		mac_credentials = MACcredentials.MACcredentials( "boo" )
		self.assertTrue( mac_credentials.owner == owner )
		self.assertTrue( mac_credentials.mac_key_identifier is not None )
		self.assertTrue( mac_credentials.mac_key is not None )
		self.assertTrue( mac_credentials.mac_algorithm is not None )
		self.assertTrue( mac_credentials.issue_time is not None )
		print mac_credentials

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File
