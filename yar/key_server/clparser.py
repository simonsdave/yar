"""This module contains all the logic required to parse the key
server's command line."""

import optparse
import logging

from dasutils import clparserutil


class CommandLineParser(optparse.OptionParser):
    """This class parses the key server's command line."""

    def __init__(self):
        optparse.OptionParser.__init__(
            self,
            "usage: %prog [options]",
            option_class=clparserutil.Option)

        default = logging.ERROR
        fmt = (
            "logging level "
            "[DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL]"
            " - default = %s"
        )
        help = fmt % logging.getLevelName(default)
        self.add_option(
            "--log",
            action="store",
            dest="logging_level",
            default=default,
            type="logginglevel",
            help=help)

        default = 8070
        help = "port - default = %d" % default
        self.add_option(
            "--port",
            action="store",
            dest="port",
            default=default,
            type=int,
            help=help)

        default = "localhost:5984/creds"
        fmt = (
            "key store - "
            "host:port/database"
            " - default = %s"
        )
        help = fmt % default
        self.add_option(
            "--key_store",
            action="store",
            dest="key_store",
            default=default,
            type="couchdb",
            help=help)
