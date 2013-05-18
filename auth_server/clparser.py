"""This module contains all the logic required to parse the authentication
server's command line."""

import optparse
import logging

import clparserutil


class CommandLineParser(optparse.OptionParser):
    """This class parses the auth server's command line."""

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
            default=logging.ERROR,
            type="logginglevel",
            help=help)

        default = 8000
        help = "port - default = %d" % default
        self.add_option(
            "--port",
            action="store",
            dest="port",
            default=default,
            type=int,
            help=help)

        default = "DAS",
        help = "app server's authorization method - default = %s" % default
        self.add_option(
            "--authmethod",
            action="store",
            dest="app_server_auth_method",
            default=default,
            help=help)

        default = "localhost:8070"
        help = "key server - default = %s" % default
        self.add_option(
            "--keyserver",
            action="store",
            dest="key_server",
            default=default,
            type="hostcolonport",
            help=help)

        default = "localhost:8080"
        help = "app server - default = %s" % default
        self.add_option(
            "--appserver",
            action="store",
            dest="app_server",
            default=default,
            type="hostcolonport",
            help=help)

        default = 30
        help = "max age (in seconds) of valid request - default = %d" % default
        self.add_option(
            "--maxage",
            action="store",
            dest="maxage",
            default=default,
            type=int,
            help=help)

        default = ["localhost:11212"]
        help = "memcached servers for nonce store - default = %s" % default
        self.add_option(
            "--noncestore",
            action="store",
            dest="nonce_store",
            default=default,
            type="memcached",
            help=help)
