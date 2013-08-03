"""This module implements a collection of utilities for unit testing yar"""

import json
import unittest
import uuid

import jsonschema

class TestCase(unittest.TestCase):

    @classmethod
    def random_non_none_non_zero_length_str(cls):
        """Return a random, non-None, non-zero-length string."""
        return str(uuid.uuid4()).replace("-", "")

    def _is_json(self, str_that_might_be_json):
        """Return ```True``` if ```str_that_might_be_json``` is a
        valid JSON string otherwise return ```False```."""
        if str_that_might_be_json is None:
            return False
        try:
            json.loads(str_that_might_be_json)
        except:
            return False
        return True

    def assertIsJSON(self, str_that_should_be_json):
        """assert that ```str_that_should_be_json``` is a
        valid JSON string."""
        self.assertTrue(self._is_json(str_that_should_be_json))

    def assertIsNotJSON(self, str_that_should_not_be_json):
        """assert that ```str_that_should_not_be_json``` is not a
        valid JSON string."""
        self.assertFalse(self._is_json(str_that_should_not_be_json))

    def _is_valid_json(self, str_that_might_be_valid_json, schema):
        """Return ```True``` is ```str_that_might_be_valid_json``` is
        a json document that is successfully validated by the 
        JSON schema ```schema```."""
        if not self._is_json(str_that_might_be_valid_json):
            return False
        try:
            jsonschema.validate(str_that_might_be_valid_json, schema)
        except:
            return False
        return True

    def assertIsValidJSON(self, str_that_should_be_valid_json, schema):
        """assert that ```str_that_should_not_be_valid_json``` is a JSON
        document and is valid according to the JSON schema ```schema```."""
        self.assertIsJSON(str_that_should_be_valid_json)
        self.assertFalse(self._is_valid_json(str_that_should_be_valid_json, schema))

    def assertIsNotValidJSON(self, str_that_should_not_be_valid_json, schema):
        """assert that ```str_that_should_not_be_valid_json``` is a JSON
        document but is not valid according to the JSON schema ```schema```."""
        self.assertIsJSON(str_that_should_not_be_valid_json)
        self.assertFalse(self._is_valid_json(str_that_should_not_be_valid_json, schema))
