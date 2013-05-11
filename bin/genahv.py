#!/usr/bin/env python
"""This module ."""

import sys
import os

import mac

#-------------------------------------------------------------------------------

def _generate_authorization_header_value(
	http_method,
	host,
	port,
	uri,
	mac_key_identifier,
	mac_key,
	mac_algorithm,
	content_type,
	body):

	ts = mac.Timestamp.generate()
	nonce = mac.Nonce.generate()
	ext = mac.Ext.generate(content_type, body)
	normalized_request_string = mac.NormalizedRequestString.generate(
		ts,
		nonce,
		http_method,
		uri,
		host,
		port,
		ext)
	my_mac = mac.MAC.generate(
		mac_key,
		mac_algorithm,
		normalized_request_string)
	rv = mac.AuthHeaderValue(
		mac_key_identifier,
		ts,
		nonce,
		ext,
		my_mac)
	return rv

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	# print 30*'-'
	# for a in sys.argv:
	# 	print ">>>%s<<<" % a
	# print 30*'-'
	number_argvs = len(sys.argv)
	if 8 != number_argvs and 9 != number_argvs:
		filename = os.path.split(sys.argv[0])[1]
		fmt = "usage: %s <http method> <host> <port> <uri> <mac key identifier> <mac key> <mac algorithm> [<content_type>]"
		print fmt % filename
		sys.exit(1)

	if 9 == number_argvs:
		content_type = sys.argv[8]
		body = sys.stdin.read()
	else:
		content_type = None
		body = None

	authorization_header_value = _generate_authorization_header_value(
		sys.argv[1],
		sys.argv[2],
		sys.argv[3],
		sys.argv[4],
		sys.argv[5],
		sys.argv[6],
		sys.argv[7],
		content_type,
		body)
	print authorization_header_value

#------------------------------------------------------------------- End-of-File
