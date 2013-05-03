#!/usr/bin/env python
"""This module ."""

import sys
import os
import logging
logging.basicConfig(level=logging.FATAL)

import mac

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	if 9 != len( sys.argv ):
		filename = os.path.split(sys.argv[0])[1]
		fmt = "usage: %s <host> <port> <http method> <uri> <ts> <nonce> <ext> <mac key> <mac algorithm>"
		print fmt % filename
		sys.exit(1)

	normalized_request_string = mac.NormalizedRequestString(
		mac.Timestamp(sys.argv[5]),
		mac.Nonce(sys.argv[6]),
		sys.argv[3],
		sys.argv[4],
		sys.argv[1],
		sys.argv[2],
		mac.Ext.compute(None, None))
	my_mac = mac.MAC.compute(
		sys.argv[7],
		sys.argv[8],
		normalized_request_string)
	print my_mac

#------------------------------------------------------------------- End-of-File
