#!/usr/bin/env python
"""This module contains a series of utilities for writing
Tornado request handlers."""

import httplib
import re
import json
import uuid
import logging

import tornado.web

#-------------------------------------------------------------------------------

class RequestHandler(tornado.web.RequestHandler):
	"""When a request handler uses this as its base class rather than
	tornado.web.RequestHandler the request handler gains access to
	a collection of useful utility methods that operate on requests
	and responses. The utility methods focus on requests and responses
	that use JSON."""

	def is_json_utf8_content_type(self):
		"""Returns True is the request's content type is UTF8 json
		otherwise False is returned."""
		content_type = self.request.headers.get("content-type", None)
		if content_type is None:
			return False
		json_utf8_content_type_reg_ex = re.compile(
			"^\s*application/json;\s+charset\=utf-{0,1}8\s*$",
			re.IGNORECASE )
		if not json_utf8_content_type_reg_ex.match(content_type):
			return False
		return True

	def get_json_request_body(self):
		"""Get the request's JSON body and convert it into a dict.
		If there's not body, the body isn't JSON, etc then return
		None otherwise return the dict."""
		if not self.is_json_utf8_content_type():
			return None

		content_length = self.request.headers.get("content-length", 0)
		if 0 == content_length:
			return None

		body = self.request.body
		if body is None:
			return None

		try:
			body_as_dict = json.loads(body)
		except:
			return None

		return body_as_dict

	def get_value_from_json_request_body(self, key, value_if_not_found=None):
		# :TODO: fix this comment 'cause it's not RST
		"""This method is a shortcut for:
		body = self.get_json_request_body()
		if body is None:
			value = value_if_not_found
		else:
			value = body.get(key, value_if_not)"""
		body_as_dict = self.get_json_request_body()
		if body_as_dict is None:
			return value_if_not_found

		return body_as_dict.get(key, value_if_not_found)

#------------------------------------------------------------------- End-of-File
