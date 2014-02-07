"""This module contains all the logic required to parse the authentication
server's command line."""

import optparse
import logging

from yar.util import clparserutil


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

        default = [("127.0.0.1", 8000)]
        help = "address:port to listen on - default = %s" % default
        self.add_option(
            "--lon",
            action="store",
            dest="listen_on",
            default=default,
            type="hostcolonportsparsed",
            help=help)

        default = "YAR",
        help = "app server's authorization method - default = %s" % default
        self.add_option(
            "--authmethod",
            action="store",
            dest="app_server_auth_method",
            default=default,
            help=help)

        default = "127.0.0.1:8070"
        help = "key server - default = %s" % default
        self.add_option(
            "--keyserver",
            action="store",
            dest="key_server",
            default=default,
            type="hostcolonport",
            help=help)

        default = "127.0.0.1:8080"
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

        default = ["127.0.0.1:11211"]
        help = "memcached servers for nonce store - default = %s" % default
        self.add_option(
            "--noncestore",
            action="store",
            dest="nonce_store",
            default=default,
            type="hostcolonports",
            help=help)
