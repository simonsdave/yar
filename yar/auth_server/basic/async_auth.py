"""This module contains the core logic for implemenation
of the basic authentication scheme."""

import base64
import logging
import re

_logger = logging.getLogger("AUTHSERVER.%s" % __name__)

# these constants define detailed authentication failure reasons
AUTH_FAILURE_DETAIL_NO_AUTH_HEADER = 0x0001
AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER_FORMAT_PRE_DECODING = 0x0002
AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER_BAD_ENCODING = 0x0003
AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER_FORMAT_POST_DECODING = 0x0004
AUTH_FAILURE_DETAIL_CREDS_NOT_FOUND = 0x0003

"""```_auth_hdr_val_reg_ex``` is used to parse the value of
the Authorization HTTP header."""
_auth_hdr_val_reg_ex = re.compile(
    "^\s*BASIC\s+(?P<api_key_colon>[^\s]+)\s*$",
    re.IGNORECASE)

"""Once the authorization header's value is base64 decoded,
```_api_key_colon_reg_ex``` is used to verify the
decoded value is in the expected format and also extract the
api key."""
_api_key_colon_reg_ex = re.compile(
    "^(?P<api_key>[^:]+):$",
    re.IGNORECASE)


class Authenticator(object):
    """Async'ly authenticate a Tornado request using the basic
    authentication scheme by
    (i) extracting and parsing the Authorization header's value,
    (ii) asking the key store for credentials matching values
    extracted from the authorization header"""

    def __init__(self, request, generate_auth_failure_debug_details):
        object.__init__(self)
        self._request = request
        self._generate_auth_failure_debug_details = \
            generate_auth_failure_debug_details

    def authenticate(self, on_auth_done):
        self._on_auth_done = on_auth_done

        auth_hdr_val = self._request.headers.get("Authorization", None)
        if auth_hdr_val is None:
            self._on_auth_done(False, AUTH_FAILURE_DETAIL_NO_AUTH_HEADER)
            return

        match = _auth_hdr_val_reg_ex.match(auth_hdr_val)
        if not match:
            self._on_auth_done(
                False,
                AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER_FORMAT_PRE_DECODING)
            return

        b64encoded_api_key_colon = match.group("api_key_colon")

        try:
            api_key_colon = base64.b64decode(b64encoded_api_key_colon)
        except TypeError:
            self._on_auth_done(
                False,
                AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER_BAD_ENCODING)
            return

        match = _api_key_colon_reg_ex.match(api_key_colon)
        if not match:
            self._on_auth_done(
                False,
                AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER_FORMAT_POST_DECODING)
            return

        api_key = match.group("api_key")

        _logger.info("api key = >>>%s<<<", api_key)

        self._on_auth_done(True, owner=api_key)
