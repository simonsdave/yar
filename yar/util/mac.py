"""This module is used to generate the message authentication code (MAC)
used in HTTP MAC access authentication scheme. See [1] for details.

[1] http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-01"""

import binascii
import datetime
import hashlib
import hmac
import logging
import os
import re
import requests
import string
import urllib2
import uuid

from keyczar import keyczar

_logger = logging.getLogger("UTIL.%s" % __name__)


def _hexify(bytes):
    """Super simple utility to turn an array of bytes in
    a hex string representation of those bytes.
    On success returns a non-None byte array.
    On failure returns None.
    Returns None if ```bytes``` is None."""
    if bytes is None:
        return None
    return binascii.b2a_hex(bytes)


def _dehexify(bytes_encoded_as_hex_string):
    """Super simple utility to do the reverse of ```_hexify()```"""
    if bytes_encoded_as_hex_string is None:
        return None
    try:
        return binascii.a2b_hex(bytes_encoded_as_hex_string)
    except TypeError:
        return None


class Nonce(str):
    """This class generates a 16 character random string intend
    for use as a nonce when computing an HMAC."""

    def __new__(cls, nonce):
        return str.__new__(cls, nonce)

    @classmethod
    def generate(cls):
        """Generate a nonce. Returns an instance of ```Nonce```"""
        return cls(_hexify(os.urandom(8)))


class Timestamp(str):
    """Represents the # of seconds since 1st Jan 1970."""

    def __new__(cls, ts):
        int(ts)
        return str.__new__(cls, ts)

    @classmethod
    def generate(cls):
        """Generate a timestamp. Returns an instance of ```Timestamp```"""
        epoch = datetime.datetime(1970, 1, 1, 0, 0, 0)
        ts = int((datetime.datetime.utcnow() - epoch).total_seconds())
        return cls(ts)


class Ext(str):
    """Implements the notion of the ext as described in
    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.1"""

    def __new__(cls, ext):
        return str.__new__(cls, ext)

    @classmethod
    def generate(cls, content_type, body):
        """Generate an "ext". Returns an instance of ```Ext```.

        The key concept behind the value of the Ext is we don't
        want to allow someone to take a correctly signed request,
        change a fundamental element of the request and then
        resend the request. The normalized request string described
        in the  MAC standard covers most of key elements of a request
        except for the request's body and content type. In this
        implementation of the MAC standard we have choose to generate
        an ext using a combination of the content type and request
        body. The algorithm for generating the ext is:

            if content_type and body are None then ext = ""
            if content_type is None then content_type = ""
            if body is None then body = ""
            ext = hex encoding of(content_type + body)

        If ```content_type``` is None it is assumed to mean that no
        content type header was supplied in the request.

        If ```body``` is None it is assumed to mean that no
        body was supplied in the request."""
        if content_type is None and body is None:
            ext = ""
        else:
            content_type_plus_body = \
                (content_type if content_type is not None else "") \
                + \
                (body if body is not None else "")
            content_type_plus_body_hash = hashlib.sha1(content_type_plus_body)
            print content_type_plus_body
            ext = content_type_plus_body_hash.hexdigest()

        return cls(ext)


class NormalizedRequestString(str):
    """Implements the notion of a normalized request string as described in
    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.2.1"""

    def __new__(cls, normalized_request_string):
        return str.__new__(cls, normalized_request_string)

    @classmethod
    def generate(cls, ts, nonce, http_method, uri, host, port, ext):
        """Generate a normalized request string.
        Returns an instance of ```NormalizedRequestString```"""
        normalized_request_string = \
            ts + '\n' + \
            nonce + '\n' + \
            http_method + '\n' + \
            uri + '\n' + \
            host + '\n' + \
            str(port) + '\n' + \
            ext + '\n'
        return cls(normalized_request_string)


class MACKeyIdentifier(str):
    """This class generates a 32 character random string intend
    for use as a MAC key identifier."""

    def __new__(cls, mac_key_identifier):
        return str.__new__(cls, mac_key_identifier)

    @classmethod
    def generate(cls):
        """Generate a mac key identifier. Returns an instance
        of ```MACKeyIdentifier```. There have been a few different
        implementations of this method. os.random() was used for
        a while but in the end the current implementation seemed
        to make the most sense because (i) nothing about the mac
        key identifier needs to be 'secure' (ii) wanted to be able
        to run a cluster of key services to generate mac key identifers
        across multiple data centers so needed an approach which
        saw a very high probability that generated mac key identifiers
        where unique."""
        return cls(uuid.uuid4().hex)


class MACKey(str):
    """This class generates a 32 character random string intend
    for use as a MAC key."""

    """# of bits in the generated key."""
    _key_size_in_bits = 256

    @classmethod
    def _is_value_ok(cls, value):
        if value is None:
            return False
        # Uses URL-safe alphabet: - replaces +, _ replaces /.
        if not re.match("^[0-9a-zA-Z\_\-]{43}$", value):
            return False
        return True

    def __new__(cls, value):
        # all of this checking of 'value' argument is here so
        # _dehexify() doesn't fail in as_keyczar_hmac_key()
        if not cls._is_value_ok(value):
            msg = "'value' error: must be a 43 character string"
            raise ValueError(msg)
        return str.__new__(cls, value)

    def as_keyczar_hmac_key(self):
        """Decode self into a instance of ```keyczar.keys.HmacKey```."""
        keyczar_hmac_key = keyczar.keys.HmacKey(
            self,
            self.__class__._key_size_in_bits)
        return keyczar_hmac_key

    @classmethod
    def generate(cls):
        """Generate a mac key. Returns an instance of ```MACKey```"""
        key = keyczar.keys.HmacKey.Generate(cls._key_size_in_bits)
        return cls(key.key_string)


class MAC(str):
    """Implements concept of a message authentication code according to
    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02"""

    """Name of algorithm used to compute the MAC."""
    algorithm = "hmac-sha-1"

    def __new__(cls, mac):
        return str.__new__(cls, mac)

    def verify(self, mac_key, mac_algorithm, normalized_request_string):
        """Generate a MAC for ```normalized_request_string``` and compare
        it to ```self```. If the MACs are equal return True otherwise
        return False.

        To prevent timing attacks this method is should be instead of
        direct MAC comparision."""
        keyczar_hmac_key = mac_key.as_keyczar_hmac_key()
        dehexified_self = _dehexify(self)
        if not dehexified_self:
            return False
        rv = keyczar_hmac_key.Verify(
            normalized_request_string,
            dehexified_self)
        return rv

    @classmethod
    def generate(cls, mac_key, mac_algorithm, normalized_request_string):
        """Generate a request's MAC given a normalized request sring (aka
        a summary of the key elements of the request, the mac key and
        the algorithm."""
        keyczar_hmac_key = mac_key.as_keyczar_hmac_key()
        return cls(_hexify(keyczar_hmac_key.Sign(normalized_request_string)))


class AuthHeaderValue(object):
    """As per http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02 create
    the value for the HTTP Authorization header using and an existing hmac."""

    def __init__(self, mac_key_identifier, ts, nonce, ext, mac):
        object.__init__(self)

        self.mac_key_identifier = mac_key_identifier
        self.ts = ts
        self.nonce = nonce
        self.ext = ext
        self.mac = mac

    def __str__(self):
        fmt = 'MAC id="%s", ts="%s", nonce="%s", ext="%s", mac="%s"'
        rv = fmt % (
            self.mac_key_identifier,
            self.ts,
            self.nonce,
            self.ext,
            self.mac)
        return rv

    @classmethod
    def parse(cls, value):
        """Parse a string which is the value from an HTTP authorization
        header. If parsing is successful create and return a AuthHeaderValue
        otherwise return None."""
        if value is None:
            return None

        reg_ex_pattern = (
            '^\s*'
            'MAC\s+'
            'id\s*\=\s*"(?P<mac_key_identifier>[^"]+)"\s*\,\s*'
            'ts\s*\=\s*"(?P<ts>[^"]+)"\s*\,\s*'
            'nonce\s*\=\s*"(?P<nonce>[^"]+)"\s*\,\s*'
            'ext\s*\=\s*"(?P<ext>[^"]*)"\s*\,\s*'
            'mac\s*\=\s*"(?P<mac>[^"]+)"\s*'
            '$'
        )
        reg_ex = re.compile(reg_ex_pattern, re.IGNORECASE)
        match = reg_ex.match(value)
        if not match:
            _logger.info(
                "Invalid format for authorization header '%s'",
                value)
            return None
        _logger.info(
            "Valid format for authorization header '%s'",
            value)

        assert 0 == match.start()
        assert len(value) == match.end()
        assert 5 == len(match.groups())

        mac_key_identifier = match.group("mac_key_identifier")
        assert mac_key_identifier
        assert 0 < len(mac_key_identifier)

        ts = match.group("ts")
        assert ts
        assert 0 < len(ts)
        ts = Timestamp(ts)

        nonce = match.group("nonce")
        assert nonce
        assert 0 < len(nonce)
        nonce = Nonce(nonce)

        ext = match.group("ext")
        assert ext is not None
        assert 0 <= len(ext)
        ext = Ext(ext)

        mac = match.group("mac")
        assert mac
        assert 0 < len(mac)
        mac = MAC(mac)

        return cls(mac_key_identifier, ts, nonce, ext, mac)


class RequestsAuth(requests.auth.AuthBase):
    """RequestsAuth allows mac authentication to be used with the
    popular Requests package. For more details on Requests authentiation
    see http://docs.python-requests.org/en/latest/user/authentication/."""

    def __init__(self, mac_key_identifier, mac_key, mac_algorithm):
        self.mac_key_identifier = mac_key_identifier
        self.mac_key = mac_key
        self.mac_algorithm = mac_algorithm

    def __call__(self, r):

        ts = Timestamp.generate()
        nonce = Nonce.generate()

        content_type = r.headers.get("content-type", None)
        ext = Ext.generate(content_type, r.body)

        parsed_url = urllib2.urlparse.urlparse(r.url)
        path = parsed_url.path
        host = parsed_url.netloc.split(":")[0]
        port = self._port(parsed_url)

        nrs = NormalizedRequestString.generate(
            ts,
            nonce,
            r.method,
            path,
            host,
            port,
            ext)
        my_mac = MAC.generate(
            self.mac_key,
            self.mac_algorithm,
            nrs)
        ahv = AuthHeaderValue(
            self.mac_key_identifier,
            ts,
            nonce,
            ext,
            my_mac)
        r.headers["Authorization"] = str(ahv)
        return r

    def _port(self, parsed_url):
        parsed_netloc = parsed_url.netloc.split(":")
        if 2 == len(parsed_netloc):
            return parsed_netloc[1]
        scheme_to_port = {
            "http": 80,
            "https": 443,
        }
        return scheme_to_port.get(parsed_url.scheme, 80)
