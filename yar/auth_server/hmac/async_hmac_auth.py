"""This module contains the core logic for implemenation
an async HMAC validation."""

import hashlib
import logging

from yar import mac
from yar.util.trhutil import get_request_host_and_port
from yar.util.trhutil import get_request_body_if_exists

from async_hmac_creds_retriever import AsyncHMACCredsRetriever
from async_nonce_checker import AsyncNonceChecker

"""To help prevent reply attacks the timestamp of all requests can
be no older than ```maxage``` seconds before the current timestamp."""
maxage = 30

_logger = logging.getLogger("AUTHSERVER.%s" % __name__)

# these constants define detailed MAC authentication failure reasons
AUTH_FAILURE_DETAIL_TS_IN_FUTURE = 0x0010 + 0x0001
AUTH_FAILURE_DETAIL_TS_OLD = 0x0010 + 0x0002
AUTH_FAILURE_DETAIL_NO_AUTH_HEADER = 0x0010 + 0x0003
AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER = 0x0010 + 0x0004
AUTH_FAILURE_DETAIL_CREDS_NOT_FOUND = 0x0010 + 0x0005
AUTH_FAILURE_DETAIL_NONCE_REUSED = 0x0010 + 0x0006
AUTH_FAILURE_DETAIL_HMACS_DO_NOT_MATCH = 0x0010 + 0x0007


class AsyncHMACAuth(object):

    def __init__(self, request):
        object.__init__(self)
        self._request = request

    def _on_async_hmac_creds_retriever_done(
        self,
        is_ok,
        mac_key_identifier,
        is_deleted=None,
        mac_algorithm=None,
        mac_key=None,
        owner=None):

        if not is_ok:
            _logger.info(
                "No MAC credentials found for '%s'",
                self._request.full_url())
            self._on_auth_done(False, AUTH_FAILURE_DETAIL_CREDS_NOT_FOUND)
            return

        (host, port) = get_request_host_and_port(
            self._request,
            "localhost",
            80)
        content_type = self._request.headers.get("Content-type", None)
        body = get_request_body_if_exists(self._request, None)
        ext = mac.Ext.generate(content_type, body)
        normalized_request_string = mac.NormalizedRequestString.generate(
            self._auth_hdr_val.ts,
            self._auth_hdr_val.nonce,
            self._request.method,
            self._request.uri,
            host,
            port,
            ext)

        macs_equal = self._auth_hdr_val.mac.verify(
            mac_key,
            mac_algorithm,
            normalized_request_string)
        if not macs_equal:
            fmt = (
                "For '%s' using MAC key identifier '%s' "
                "MAC in request '%s' doesn't match computed MAC"
            )
            _logger.info(
                fmt,
                self._request.full_url(),
                mac_key_identifier,
                self._auth_hdr_val.mac)

            # When an authentication failure occurs it can be super hard
            # to figure out the root cause of the error. This method is called
            # on authentication failure and, if logging is set to at least
            # debug, a whole series of HTTP headers are set to return the
            # core elements that are used to generate the HMAC.
            auth_failure_debug_details = {}

            if body:
                sha1_of_body = hashlib.sha1(body).hexdigest()
                auth_failure_debug_details["BODY-SHA1"] = sha1_of_body
                auth_failure_debug_details["BODY-LEN"] = len(body)

            auth_failure_debug_details["MAC-KEY-IDENTIFIER"] = mac_key_identifier
            auth_failure_debug_details["MAC-KEY"] = mac_key
            auth_failure_debug_details["MAC-ALGORITHM"] = mac_algorithm
            auth_failure_debug_details["HOST"] = host
            auth_failure_debug_details["PORT"] = port
            auth_failure_debug_details["CONTENT-TYPE"] = content_type
            auth_failure_debug_details["REQUEST-METHOD"] = self._request.method
            auth_failure_debug_details["URI"] = self._request.uri
            auth_failure_debug_details["TIMESTAMP"] = self._auth_hdr_val.ts
            auth_failure_debug_details["NONCE"] = self._auth_hdr_val.nonce
            auth_failure_debug_details["EXT"] = ext
            auth_failure_debug_details["MAC"] = mac.MAC.generate(
                mac_key,
                mac_algorithm,
                normalized_request_string)

            # end of pumping out debug headers - returning to regular headers
            self._on_auth_done(
                False,
                auth_failure_detail=AUTH_FAILURE_DETAIL_HMACS_DO_NOT_MATCH,
                auth_failure_debug_details=auth_failure_debug_details)
            return

        _logger.info(
            "Authorization successful for '%s' and MAC '%s'",
            self._request.full_url(),
            self._auth_hdr_val.mac)

        self._on_auth_done(True, owner=owner)

    def _on_async_nonce_checker_done(self, is_ok):
        """this callback is invoked when AsyncNonceChecker has finished.
        ```is_ok``` will be ```True`` AsyncNonceChecker has confirmed that
         the curent request's nonce+mac_key_identifier pair hasn't been
        seen before."""
        if not is_ok:
            _logger.info("Nonce '%s' reused", self._auth_hdr_val.nonce)
            self._on_auth_done(False, AUTH_FAILURE_DETAIL_NONCE_REUSED)
            return

        # basic request looks good
        #
        # 1/ authentication header found and format is valid
        # 2/ timestamp is recent
        # 3/ nonce has not previous been used by the mac key identifier
        #
        # next steps is to retrieve the credentials associated with
        # the request's mac key identifier and confirm the request's
        # MAC is valid ie. final step in confirming the sender's identity
        acr = AsyncHMACCredsRetriever(self._auth_hdr_val.mac_key_identifier)
        acr.fetch(self._on_async_hmac_creds_retriever_done)

    def authenticate(self, on_auth_done):
        self._on_auth_done = on_auth_done

        auth_hdr_val = self._request.headers.get("Authorization", None)
        if auth_hdr_val is None:
            self._on_auth_done(False, AUTH_FAILURE_DETAIL_NO_AUTH_HEADER)
            return

        self._auth_hdr_val = mac.AuthHeaderValue.parse(auth_hdr_val)
        if self._auth_hdr_val is None:
            self._on_auth_done(False, AUTH_FAILURE_DETAIL_INVALID_AUTH_HEADER)
            return

        # confirm the request isn't old which is important in protecting
        # against reply attacks - also requests with timestamps in the
        # future are also
        now = mac.Timestamp.generate()
        age = int(now) - int(self._auth_hdr_val.ts)
        if age < 0:
            # :TODO: timestamp in the future - bad - clocks out of sync?
            # do we want to allow clocks to be a wee bit ouf of sync?
            self._on_auth_done(False, AUTH_FAILURE_DETAIL_TS_IN_FUTURE)
            return

        if maxage < age:
            self._on_auth_done(False, AUTH_FAILURE_DETAIL_TS_OLD)
            return

        # time to confirm if the nonce in the request has been used
        # before. this means async'ly calling out to the memcached
        # cluster which stores previously used nonce+mac_key_identifer
        # combinations
        anc = AsyncNonceChecker(
            self._auth_hdr_val.mac_key_identifier,
            self._auth_hdr_val.nonce)
        anc.fetch(self._on_async_nonce_checker_done)
