"""This module contains a collection of unit tests which
validate lib/jsonschemas.py"""

import unittest
import json
import uuid
import sys
import os

import jsonschema

from yar.key_server import jsonschemas
from yar.util import mac
from yar.util import basic


class KeyServerCreateCredsRequestTestCase(unittest.TestCase):

    def _good_request(self):
        return {
            "principal": "simonsdave@gmail.com",
        }

    def _validate(self, request):
        jsonschema.validate(
            request,
            jsonschemas.create_creds_request)

    def test_request_all_good(self):
        request = self._good_request()
        self._validate(request)

    def test_request_empty(self):
        request = self._good_request()
        self._validate(request)
        del request["principal"]
        self.assertEquals(0, len(request))
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(request)

    def test_request_zero_length_principal(self):
        request = self._good_request()
        self._validate(request)
        request["principal"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(request)

    def test_request_extra_properties(self):
        request = self._good_request()
        self._validate(request)
        request[str(uuid.uuid4())] = "bindle@berrypie.com"
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(request)


class KeyServerGetCredsResponseTestCase(unittest.TestCase):

    def _uuid(self):
        return str(uuid.uuid4())

    def _generate_good_response(self):
        return None

    def _validate(self, response):
        jsonschema.validate(
            response,
            jsonschemas.get_creds_response)

    def test_all_good(self):
        response = self._generate_good_response()
        if not response:
            # :TODO: crappy way to do this - how do we avoid nosetests selecting
            # this abstract base class as a real test case class
            return
        self._validate(response)

    def test_is_deleted_is_not_boolean(self):
        response = self._generate_good_response()
        if not response:
            # :TODO: crappy way to do this - how do we avoid nosetests selecting
            # this abstract base class as a real test case class
            return
        self._validate(response)
        response["is_deleted"] = self._uuid()
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)

    def test_invalid_principal(self):
        response = self._generate_good_response()
        if not response:
            # :TODO: crappy way to do this - how do we avoid nosetests selecting
            # this abstract base class as a real test case class
            return
        self._validate(response)
        response["principal"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)
        del response["principal"]
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)

    def test_invalid_links(self):
        # :TODO: this should be a more exhaustive test
        response = self._generate_good_response()
        if not response:
            # :TODO: crappy way to do this - how do we avoid nosetests selecting
            # this abstract base class as a real test case class
            return
        self._validate(response)
        response["links"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)
        del response["links"]
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)

    def test_extra_properties(self):
        response = self._generate_good_response()
        if not response:
            # :TODO: crappy way to do this - how do we avoid nosetests selecting
            # this abstract base class as a real test case class
            return
        self._validate(response)
        response[self._uuid()] = self._uuid()
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)


class KeyServerGetBasicCredsResponseTestCase(KeyServerGetCredsResponseTestCase):

    def _generate_good_response(self):
        api_key = basic.APIKey.generate()
        return {
            "basic": {
                "api_key": str(api_key),
            },
            "is_deleted": True,
            "principal": "simonsdave@gmail.com",
            "links": {
                "self": {
                    "href": "http://127.0.0.1:8070/v1.0/creds/f274d56f213faa731e97735f790ddc89"
                }
            }
        }

    def test_invalid_api_key(self):
        response = self._generate_good_response()
        self._validate(response)

        response["basic"]["api_key"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)

        del response["basic"]["api_key"]
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)


class KeyServerGetHMACCredsResponseTestCase(KeyServerGetCredsResponseTestCase):

    def _generate_good_response(self):
        mac_key = mac.MACKey.generate()
        mac_key_identifier = mac.MACKeyIdentifier.generate()
        return {
            "hmac": {
                "mac_algorithm": "hmac-sha-1",
                "mac_key": str(mac_key),
                "mac_key_identifier": str(mac_key_identifier),
            },
            "is_deleted": True,
            "principal": "simonsdave@gmail.com",
            "links": {
                "self": {
                    "href": "http://127.0.0.1:8070/v1.0/creds/f274d56f213faa731e97735f790ddc89"
                }
            }
        }

    def test_sha_256_algorithm(self):
        response = self._generate_good_response()
        self._validate(response)
        response["hmac"]["mac_algorithm"] = "hmac-sha-256"
        self._validate(response)

    def test_invalid_algorithm(self):
        response = self._generate_good_response()
        self._validate(response)
        response["hmac"]["mac_algorithm"] = self._uuid()
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)
        response["hmac"]["mac_algorithm"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)

    def test_invalid_mac_key(self):
        response = self._generate_good_response()
        self._validate(response)
        response["hmac"]["mac_key"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)
        del response["hmac"]["mac_key"]
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)

    def test_invalid_mac_key_identifier(self):
        response = self._generate_good_response()
        self._validate(response)
        response["hmac"]["mac_key_identifier"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)
        del response["hmac"]["mac_key_identifier"]
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)
