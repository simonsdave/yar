"""This module contains all the logic required to parse the app
server's command line."""


import re
import logging
import optparse

import clparserutil


class CommandLineParser(optparse.OptionParser):

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
            default=8080,
            type=int,
            help="port - default = 8080")
