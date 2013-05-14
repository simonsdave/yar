#!/usr/bin/env python

import unittest
import json

import jsonschema

import jsonschemas

#-------------------------------------------------------------------------------

class KeyServerCreateCredsRequestTestCase(unittest.TestCase):
	
	def test_key_server_create_creds_request_all_good(self):
		request = {"owner": "simonsdave@gmail.com"}
		jsonschema.validate(
			request,
			jsonschemas.key_server_create_creds_request)

	def test_key_server_create_creds_request_empty(self):
		request = {"owner": "simonsdave@gmail.com"}
		jsonschema.validate(
			request,
			jsonschemas.key_server_create_creds_request)
		del request["owner"]
		self.assertEquals(0, len(request))
		with self.assertRaises(jsonschema.ValidationError):
			jsonschema.validate(
				request,
				jsonschemas.key_server_create_creds_request)

	def test_key_server_create_creds_request_zero_length_owner(self):
		request = {"owner": "simonsdave@gmail.com"}
		jsonschema.validate(
			request,
			jsonschemas.key_server_create_creds_request)
		request["owner"] = ""
		with self.assertRaises(jsonschema.ValidationError):
			jsonschema.validate(
				request,
				jsonschemas.key_server_create_creds_request)

	def test_key_server_create_creds_request_more_that_just_owner(self):
		request = {"owner": "simonsdave@gmail.com"}
		jsonschema.validate(
			request,
			jsonschemas.key_server_create_creds_request)
		request["dave"] = "bindle@berrypie.com"
		with self.assertRaises(jsonschema.ValidationError):
			jsonschema.validate(
				request,
				jsonschemas.key_server_create_creds_request)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	unittest.main()

#------------------------------------------------------------------- End-of-File

