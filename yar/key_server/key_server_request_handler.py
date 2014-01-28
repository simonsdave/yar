"""This module contains the key server's primary
Tornado request handler logic."""

import httplib
import logging

import tornado.web

from async_creds_creator import AsyncCredsCreator
from async_creds_retriever import AsyncCredsRetriever
from async_creds_deleter import AsyncCredsDeleter
from yar.key_server import jsonschemas
from yar.util import trhutil

_logger = logging.getLogger("KEYSERVER.%s" % __name__)

"""Format of this string is host:port/database. It's used to construct
a URL when talking to the key store."""
_key_store = "localhost:5984/creds"

"""The key server's mainline should use this URL spec
to describe the URLs that ```RequestHandler``` can
correctly service."""
url_spec = r"/v1.0/creds(?:/([^/]+))?"


class RequestHandler(trhutil.RequestHandler):

    @tornado.web.asynchronous
    def get(self, key=None):
        is_filter_out_deleted = False \
            if self.get_argument("deleted", None) \
            else True
        acr = AsyncCredsRetriever(_key_store)
        acr.fetch(
            self._on_async_creds_retrieve_done,
            key=key,
            owner=self.get_argument("owner", None),
            is_filter_out_deleted=is_filter_out_deleted,
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
            self._add_links_to_creds_dict(creds)
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
            body["owner"],
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
        print "+"*80
        print creds
        print "+"*80
        assert creds is not None
        if "hmac" in creds:
            key = creds["hmac"]["mac_key_identifier"]
        else:
            key = creds["basic"]["api_key"]
        assert key is not None
        location = "%s/%s" % (self.request.full_url(), key)
        creds["links"] = {"self": {"href": location}}
        return location
