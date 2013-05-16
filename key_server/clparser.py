"""This module contains all the logic required to parse the key
server's command line."""

import optparse
import re
import logging

import clparserutil


class CommandLineParser(optparse.OptionParser):
    """This class parses the key server's command line."""

    def __init__(self):
        optparse.OptionParser.__init__(
            self,
            "usage: %prog [options]",
            option_class=clparserutil.Option)

        help = (
            "logging level "
            "[DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL]"
            " - default = ERRROR"
        )
        self.add_option(
            "--log",
            action="store",
            dest="logging_level",
            default=logging.ERROR,
            type="logginglevel",
            help=help)

        self.add_option(
            "--port",
            action="store",
            dest="port",
            default=8070,
            type=int,
            help="port - default = 8070")

        help = (
            "key store - "
            "host:port/database"
            " - default = localhost:5984/creds"
        )
        self.add_option(
            "--key_store",
            action="store",
            dest="key_store",
            default="localhost:5984/creds",
            type="couchdb",
            help=help)
