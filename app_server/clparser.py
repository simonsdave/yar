"""This module contains all the logic required to parse the app
server's command line."""

import logging
import optparse
import re

import clparserutil


class CommandLineParser(optparse.OptionParser):

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

        default = 8080
        help="port - default = %d" % default
        self.add_option(
            "--port",
            action="store",
            dest="port",
            default=default,
            type=int,
            help=help)
