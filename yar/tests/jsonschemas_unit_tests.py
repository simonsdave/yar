"""This module contains a collection of unit tests which
validate lib/jsonschemas.py"""

import unittest
import json
import uuid
import sys
import os

import jsonschema

from yar import jsonschemas
from yar import mac


class KeyServerCreateCredsRequestTestCase(unittest.TestCase):

    def _good_request(self):
        return {
            "owner": "simonsdave@gmail.com",
        }

    def _validate(self, request):
        jsonschema.validate(
            request,
            jsonschemas.key_server_create_creds_request)

    def test_request_all_good(self):
        request = self._good_request()
        self._validate(request)

    def test_request_empty(self):
        request = self._good_request()
        self._validate(request)
        del request["owner"]
        self.assertEquals(0, len(request))
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(request)

    def test_request_zero_length_owner(self):
        request = self._good_request()
        self._validate(request)
        request["owner"] = ""
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

    def _good_response(self, is_hmac_sha_1=True):
        mac_algorithm = "hmac-sha-1" if is_hmac_sha_1 else "hmac-sha-256"
        return {
            "is_deleted": True,
            "mac_algorithm": mac_algorithm,
            "mac_key": str(mac.MACKey.generate()),
            "mac_key_identifier": str(mac.MACKeyIdentifier.generate()),
            "owner": "simonsdave@gmail.com",
            "links": {
                "self": {
                    "href": "http://localhost:8070/v1.0/creds/f274d56f213faa731e97735f790ddc89"
                    }
                }
            }

    def _validate(self, response):
        jsonschema.validate(
            response,
            jsonschemas.key_server_get_creds_response)

    def test_all_good(self):
        response = self._good_response()
        self._validate(response)

    def test_is_deleted_is_not_boolean(self):
        response = self._good_response()
        self._validate(response)
        response["is_deleted"] = self._uuid()
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)

    def test_invalid_algorithm(self):
        response = self._good_response(is_hmac_sha_1=True)
        self._validate(response)
        response = self._good_response(is_hmac_sha_1=False)
        self._validate(response)
        response["mac_algorithm"] = self._uuid()
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)
        response["mac_algorithm"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)

    def test_invalid_mac_key(self):
        response = self._good_response()
        self._validate(response)
        response["mac_key"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)
        del response["mac_key"]
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)

    def test_invalid_mac_key_identifier(self):
        response = self._good_response()
        self._validate(response)
        response["mac_key_identifier"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)
        del response["mac_key_identifier"]
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)

    def test_invalid_owner(self):
        response = self._good_response()
        self._validate(response)
        response["owner"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)
        del response["owner"]
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)

    def test_invalid_links(self):
        # :TODO: this should be a more exhaustive test
        response = self._good_response()
        self._validate(response)
        response["links"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)
        del response["links"]
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)

    def test_extra_properties(self):
        response = self._good_response()
        self._validate(response)
        response[self._uuid()] = self._uuid()
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(response)
