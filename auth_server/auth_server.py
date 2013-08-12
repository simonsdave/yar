#!/usr/bin/env python
"""This module contains the core logic for the authenication server.
The server uses implements MAC Access Authentication."""

import logging

import tornado.httpserver
import tornado.web

import tsh

import async_app_server_forwarder
import async_creds_retriever
import async_hmac_auth
import async_nonce_checker
import auth_server_request_handler
import clparser

_logger = logging.getLogger("AUTHSERVER.%s" % __name__)

if __name__ == "__main__":
    clp = clparser.CommandLineParser()
    (clo, cla) = clp.parse_args()

    tsh.install_handler()

    logging.basicConfig(level=clo.logging_level)

    fmt = (
        "Auth Server listening on {clo.port} "
        "using Nonce Store {clo.nonce_store}, "
        "Key Server '{clo.app_server}' "
        "and App Server '{clo.app_server}'"
    )
    _logger.info(fmt.format(clo=clo))

    async_creds_retriever.key_server = clo.key_server
    async_hmac_auth.maxage = clo.maxage
    async_nonce_checker.nonce_store = clo.nonce_store
    async_app_server_forwarder.app_server = clo.app_server
    async_app_server_forwarder.auth_method = clo.app_server_auth_method

    handlers = [
        (r".*", auth_server_request_handler.RequestHandler),
    ]
    app = tornado.web.Application(handlers=handlers)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(clo.port)
    tornado.ioloop.IOLoop.instance().start()
