"""This module contains all the logic required to parse the key
store installer's command line."""

import logging
import optparse

from yar.util import clparserutil


class CommandLineParser(optparse.OptionParser):

    def __init__(self):

        description = (
            "The Key Store Installer is a utility used to create "
            "and/or delete the CouchDB database that implements "
            "yar's Key Store."
        )
        optparse.OptionParser.__init__(
            self,
            "usage: %prog [options]",
            description=description,
            option_class=clparserutil.Option)

        default = logging.ERROR
        fmt = (
            "logging level [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL] - "
            "default = %s"
        )
        help = fmt % logging.getLevelName(default)
        self.add_option(
            "--log",
            action="store",
            dest="logging_level",
            default=default,
            type="logginglevel",
            help=help)

        default = "localhost:5984"
        help = "where's CouchDB running - default = %s" % default
        self.add_option(
            "--host",
            action="store",
            dest="host",
            default=default,
            type="hostcolonport",
            help=help)

        default = "creds"
        help = "database - default = %s" % default
        self.add_option(
            "--database",
            action="store",
            dest="database",
            default=default,
            type="string",
            help=help)

        default = False
        help = "delete before creating key store - default = %s" % default
        self.add_option(
            "--delete",
            action="store",
            dest="delete",
            default=default,
            type="boolean",
            help=help)

        default = True,
        help = "create key store - default = %s" % default
        self.add_option(
            "--create",
            action="store",
            dest="create",
            default=default,
            type="boolean",
            help=help)
