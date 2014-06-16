"""This module contains the key service's primary
Tornado request handler logic."""

import urllib
import httplib
import logging

import tornado.web

from async_creds_creator import AsyncCredsCreator
from async_creds_retriever import AsyncCredsRetriever
from async_creds_deleter import AsyncCredsDeleter
from yar.key_service import jsonschemas
from yar.util import trhutil

_logger = logging.getLogger("KEYSERVICE.%s" % __name__)

"""Format of this string is host:port/database. It's used to construct
a URL when talking to the key store."""
_key_store = "127.0.0.1:5984/creds"

"""The key service's mainline should use this URL spec
to describe the URLs that ```RequestHandler``` can
correctly service."""
url_spec = r"/v1.0/creds(?:/([^/]+))?"


class RequestHandler(trhutil.RequestHandler):

    @tornado.web.asynchronous
    def get(self, key=None):
        principal = self.get_argument("principal", None)

        #
        # it's only valid to ask for a specific set of credentials
        # (ie key != None) **or** all the credentials associated with
        # a specific principal.
        #
        if (not key and not principal) or (key and principal):
            self.set_status(httplib.BAD_REQUEST)
            self.finish()
            return

        acr = AsyncCredsRetriever(_key_store)
        acr.fetch(
            self._on_async_creds_retrieve_done,
            key=key,
            principal=principal,
            is_filter_out_non_model_properties=True)

    def _on_async_creds_retrieve_done(self, creds, is_creds_collection):
        if creds is None:
            self.set_status(httplib.NOT_FOUND)
            self.finish()
            return

        if is_creds_collection:
            for each_creds in creds:
                self._add_links_to_creds_dict(each_creds)
            creds = {"creds": creds}
        else:
            location = self._add_links_to_creds_dict(creds)
            self.set_header("Location", location)
        self.write(creds)
        self.finish()

    @tornado.web.asynchronous
    def post(self, key=None):
        if key is not None:
            self.set_status(httplib.METHOD_NOT_ALLOWED)
            self.finish()
            return

        body = self.get_json_request_body(
            None,
            jsonschemas.create_creds_request)
        if not body:
            self.set_status(httplib.BAD_REQUEST)
            self.finish()
            return

        acc = AsyncCredsCreator(_key_store)
        acc.create(
            body["principal"],
            body.get("auth_scheme", "basic"),
            self._on_async_creds_create_done)

    def _on_async_creds_create_done(self, creds):
        if creds is None:
            self.set_status(httplib.INTERNAL_SERVER_ERROR)
            self.finish()
            return

        location = self._add_links_to_creds_dict(creds)
        self.set_header("Location", location)
        self.write(creds)
        self.set_status(httplib.CREATED)
        self.finish()

    @tornado.web.asynchronous
    def delete(self, key=None):
        if key is None:
            self.set_status(httplib.METHOD_NOT_ALLOWED)
            self.finish()
            return

        acd = AsyncCredsDeleter(_key_store)
        acd.delete(
            key,
            self._on_async_creds_delete_done)

    def _on_async_creds_delete_done(self, isok):
        if isok is None:
            status = httplib.INTERNAL_SERVER_ERROR
        else:
            status = httplib.OK if isok else httplib.NOT_FOUND

        self.set_status(status)
        self.finish()

    def _add_links_to_creds_dict(self, creds):
        """Add HATEOAS style links to ```creds```."""

        key = self._key_from_creds(creds)

        # This method is called either because something asked
        # (i) to create a key (ii) get a collection of creds
        # (iii) get a specific set of creds. (i) and (ii)
        # are requests made to the creds collection resource
        # and (iii) is made to the resource itself. It's
        # essential to understand these request patterns in
        # order to understand this method's code."""

        (url, _) = urllib.splitquery(self.request.full_url())
        location = url if url.endswith(key) else "%s/%s" % (url, key)

        creds["links"] = {"self": {"href": location}}
        return location

    def _key_from_creds(self, creds):
        """```creds``` is a set of creds in a dict.
        If the credentials are for the MAC authentication scheme
        return the mac key identifier.
        If the credentials are for the BASIC authentication scheme
        return the api key."""

        if "mac" in creds:
            return creds["mac"]["mac_key_identifier"]

        return creds["basic"]["api_key"]
