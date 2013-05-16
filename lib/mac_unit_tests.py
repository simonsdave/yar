"""This module contains a series of unit tests which
validate lib/mac.py"""


import logging
logging.basicConfig(level=logging.FATAL)
import unittest
import string
import time
import uuid
import hashlib
import base64
import json

import mac


class MACKeyTestCase(unittest.TestCase):

    def test_generate_returns_non_none_MACKey(self):
        mac_key = mac.MACKey.generate()
        self.assertIsNotNone(mac_key)
        self.assertEqual(mac_key.__class__, mac.MACKey)

    def test_created_with_explicit_good_value(self):
        value = '90ac4f'
        mac_key = mac.MACKey(value)
        self.assertIsNotNone(mac_key)
        self.assertEqual(mac_key, value)

    def test_created_with_explicit_non_hex_value(self):
        with self.assertRaises(ValueError):
            value = 'dave'
            mac_key = mac.MACKey(value)

    def test_created_with_zero_length_value(self):
        with self.assertRaises(ValueError):
            value = ""
            mac_key = mac.MACKey(value)

    def test_created_with_explicit_old_length_value(self):
        with self.assertRaises(ValueError):
            value = '12a'
            mac_key = mac.MACKey(value)

    def test_created_with_explicit_none_value(self):
        with self.assertRaises(ValueError):
            value = None
            mac_key = mac.MACKey(value)


class MACKeyIdentifierTestCase(unittest.TestCase):

    def test_generate_returns_non_none_MACKeyIdentifier(self):
        mac_key_identifier = mac.MACKeyIdentifier.generate()
        self.assertIsNotNone(mac_key_identifier)
        self.assertEqual(mac_key_identifier.__class__, mac.MACKeyIdentifier)
        self.assertEqual(32, len(mac_key_identifier))

    def test_created_with_explicit_content(self):
        content = 'dave was here'
        mac_key_identifier = mac.MACKeyIdentifier(content)
        self.assertIsNotNone(mac_key_identifier)
        self.assertEqual(mac_key_identifier, content)


class NonceTestCase(unittest.TestCase):

    def test_generate_returns_non_none_Nonces(self):
        nonce = mac.Nonce.generate()
        self.assertIsNotNone(nonce)
        self.assertEqual(nonce.__class__, mac.Nonce)
        self.assertEqual(16, len(nonce))

    def test_created_with_explicit_content(self):
        content = 'dave was here'
        nonce = mac.Nonce(content)
        self.assertIsNotNone(nonce)
        self.assertEqual(nonce, content)


class TimestampTestCase(unittest.TestCase):

    def test_gen_returns_non_none_ts_which_represents_int(self):
        ts = mac.Timestamp.generate()
        self.assertIsNotNone(ts)
        self.assertEqual(ts.__class__, mac.Timestamp)
        self.assertTrue(0 < len(ts))
        self.assertEqual(int, int(ts).__class__)

    def test_created_with_explicit_content(self):
        content = '45'
        ts = mac.Timestamp(content)
        self.assertIsNotNone(ts)
        self.assertEqual(ts, content)

    def test_conversion_to_int(self):
        value = 45
        ts = mac.Timestamp(value)
        self.assertIsNotNone(ts)
        self.assertEqual(ts.__class__, mac.Timestamp)
        self.assertEqual(int(ts), value)

    def test_create_with_non_int(self):
        with self.assertRaises(ValueError):
            value = "dave"
            ts = mac.Timestamp(value)


class ExtTestCase(unittest.TestCase):

    def test_content_type_and_body_none_is_zero_length_ext(self):
        content_type = None
        body = None
        ext = mac.Ext.generate(content_type, body)
        self.assertIsNotNone(ext)
        self.assertEqual(ext, "")

    def test_content_type_not_none_and_body_none_is_zero_length_ext(self):
        content_type = "dave was here"
        body = None
        ext = mac.Ext.generate(content_type, body)
        self.assertIsNotNone(ext)
        self.assertEqual(ext, "")

    def test_content_type_none_and_body_not_none_is_zero_length_ext(self):
        content_type = None
        body = "dave was here"
        ext = mac.Ext.generate(content_type, body)
        self.assertIsNotNone(ext)
        self.assertEqual(ext, "")

    def test_content_type_and_body_not_none_is_sha1_of_both(self):
        content_type = "hello world!"
        body = "dave was here"
        ext = mac.Ext.generate(content_type, body)
        self.assertIsNotNone(ext)
        hash = hashlib.new('sha1', content_type + body)
        self.assertEqual(ext, hash.hexdigest())

    def test_created_with_explicit_content(self):
        content = "abc"
        ext = mac.Ext(content)
        self.assertIsNotNone(ext)
        self.assertEqual(content, ext)


class AuthHeaderValueTestCase(unittest.TestCase):

    def _uuid(self):
        return str(uuid.uuid4()).replace("-", "")

    def _create_ahv_str(self, mac_key_identifier, ts, nonce, ext, my_mac):
        fmt = 'MAC id="%s", ts="%s", nonce="%s", ext="%s", mac="%s"'
        return fmt % (mac_key_identifier, ts, nonce, ext, my_mac)

    def test_ctr_correct_property_assignment(self):
        mac_key_identifier = self._uuid()
        ts = self._uuid()
        nonce = self._uuid()
        ext = self._uuid()
        my_mac = self._uuid()
        ah = mac.AuthHeaderValue(mac_key_identifier, ts, nonce, ext, my_mac)
        self.assertEqual(ah.mac_key_identifier, mac_key_identifier)
        self.assertEqual(ah.ts, ts)
        self.assertEqual(ah.nonce, nonce)
        self.assertEqual(ah.ext, ext)
        self.assertEqual(ah.mac, my_mac)

    def test_parse_generated_value_for_get(self):
        ts = mac.Timestamp.generate()
        nonce = mac.Nonce.generate()
        http_method = "GET"
        uri = "/whatever"
        host = "localhost"
        port = 8080
        content_type = None
        body = None
        ext = mac.Ext.generate(content_type, body)
        normalized_request_string = mac.NormalizedRequestString.generate(
            ts,
            nonce,
            http_method,
            uri,
            host,
            port,
            ext)
        mac_key = mac.MACKey.generate()
        mac_algorithm = mac.MAC.algorithm
        my_mac = mac.MAC.generate(
            mac_key,
            mac_algorithm,
            normalized_request_string)
        mac_key_identifier = mac.MACKeyIdentifier.generate()
        ahv = mac.AuthHeaderValue(
            mac_key_identifier,
            ts,
            nonce,
            ext,
            my_mac)
        pahv = mac.AuthHeaderValue.parse(str(ahv))
        self.assertIsNotNone(pahv)
        self.assertEqual(pahv.mac_key_identifier, ahv.mac_key_identifier)
        self.assertEqual(pahv.ts, ahv.ts)
        self.assertEqual(pahv.nonce, ahv.nonce)
        self.assertEqual(pahv.ext, ahv.ext)
        self.assertEqual(pahv.mac, ahv.mac)

    def test_parse_generated_value_for_post(self):
        ts = mac.Timestamp.generate()
        nonce = mac.Nonce.generate()
        http_method = "POST"
        uri = "/whatever"
        host = "localhost"
        port = 8080
        content_type = "application/json;charset=utf-8"
        body = json.dumps({"dave": "was", "there": "you", "are": 42})
        ext = mac.Ext.generate(content_type, body)
        normalized_request_string = mac.NormalizedRequestString.generate(
            ts,
            nonce,
            http_method,
            uri,
            host,
            port,
            ext)
        mac_key = mac.MACKey.generate()
        mac_algorithm = mac.MAC.algorithm
        my_mac = mac.MAC.generate(
            mac_key,
            mac_algorithm,
            normalized_request_string)
        mac_key_identifier = mac.MACKeyIdentifier.generate()
        ahv = mac.AuthHeaderValue(
            mac_key_identifier,
            ts,
            nonce,
            ext,
            my_mac)
        pahv = mac.AuthHeaderValue.parse(str(ahv))
        self.assertIsNotNone(pahv)
        self.assertEqual(pahv.mac_key_identifier, ahv.mac_key_identifier)
        self.assertEqual(pahv.ts, ahv.ts)
        self.assertEqual(pahv.nonce, ahv.nonce)
        self.assertEqual(pahv.ext, ahv.ext)
        self.assertEqual(pahv.mac, ahv.mac)

    def test_parse_with_empty_mac_key_identifier(self):
        mac_key_identifier = ""
        ts = self._uuid()
        nonce = self._uuid()
        ext = self._uuid()
        my_mac = self._uuid()
        ahv_str = self._create_ahv_str(
            mac_key_identifier,
            ts,
            nonce,
            ext,
            my_mac)
        self.assertIsNone(mac.AuthHeaderValue.parse(ahv_str))

    def test_parse_with_empty_timestamp(self):
        mac_key_identifier = self._uuid()
        ts = ""
        nonce = self._uuid()
        ext = self._uuid()
        my_mac = self._uuid()
        ahv_str = self._create_ahv_str(
            mac_key_identifier,
            ts,
            nonce,
            ext,
            my_mac)
        self.assertIsNone(mac.AuthHeaderValue.parse(ahv_str))

    def test_parse_with_empty_nonce(self):
        mac_key_identifier = self._uuid()
        ts = self._uuid()
        nonce = ""
        ext = self._uuid()
        my_mac = self._uuid()
        ahv_str = self._create_ahv_str(
            mac_key_identifier,
            ts,
            nonce,
            ext,
            my_mac)
        self.assertIsNone(mac.AuthHeaderValue.parse(ahv_str))

    def test_parse_with_empty_mac(self):
        mac_key_identifier = self._uuid()
        ts = self._uuid()
        nonce = self._uuid()
        ext = self._uuid()
        my_mac = ""
        ahv_str = self._create_ahv_str(
            mac_key_identifier,
            ts,
            nonce,
            ext,
            my_mac)
        self.assertIsNone(mac.AuthHeaderValue.parse(ahv_str))

    def test_parse_none(self):
        self.assertIsNone(mac.AuthHeaderValue.parse(None))

    def test_parse_zero_length_string(self):
        self.assertIsNone(mac.AuthHeaderValue.parse(""))

    def test_parse_random_string(self):
        self.assertIsNone(mac.AuthHeaderValue.parse(self._uuid()))


class MACTestCase(unittest.TestCase):

    def test_content_type_and_body_none_is_zero_length_ext(self):
        ts = mac.Timestamp.generate()
        nonce = mac.Nonce.generate()
        http_method = "POST"
        uri = "/whatever"
        host = "localhost"
        port = 8080
        content_type = "application/json;charset=utf-8"
        body = json.dumps({"dave": "was", "there": "you", "are": 42})
        ext = mac.Ext.generate(content_type, body)
        normalized_request_string = mac.NormalizedRequestString.generate(
            ts,
            nonce,
            http_method,
            uri,
            host,
            port,
            ext)
        mac_key = mac.MACKey.generate()
        self.assertIsNotNone(mac_key)
        my_mac = mac.MAC.generate(
            mac_key,
            mac.MAC.algorithm,
            normalized_request_string)
        self.assertIsNotNone(my_mac)
        verify_rv = my_mac.verify(
            mac_key,
            mac.MAC.algorithm,
            normalized_request_string)
        self.assertTrue(verify_rv)
        normalized_request_string = mac.NormalizedRequestString.generate(
            ts,
            nonce,
            http_method,
            uri,
            host,
            port + 1,    # <<< note this change
            ext)
        verify_rv = my_mac.verify(
            mac_key,
            mac.MAC.algorithm,
            normalized_request_string)
        self.assertFalse(verify_rv)
