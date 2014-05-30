"""This module contains all the logic required to parse the
auth service's command line."""

import optparse
import logging

from yar.util import clparserutil


class CommandLineParser(optparse.OptionParser):
    """This class parses the auth service's command line."""

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

        default = "127.0.0.1:8000"
        help = "address:port to listen on - default = %s" % default
        self.add_option(
            "--lon",
            action="store",
            dest="listen_on",
            default=default,
            type="hostcolonportparsed",
            help=help)

        default = "YAR"
        help = "app service's authorization method - default = %s" % default
        self.add_option(
            "--appserviceauthmethod",
            action="store",
            dest="app_service_auth_method",
            default=default,
            type="string",
            help=help)

        default = "127.0.0.1:8070"
        help = "key service - default = %s" % default
        self.add_option(
            "--keyservice",
            action="store",
            dest="key_service",
            default=default,
            type="hostcolonport",
            help=help)

        default = "127.0.0.1:8080"
        help = "app service - default = %s" % default
        self.add_option(
            "--appserver",
            action="store",
            dest="app_service",
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

        default = None
        help = "syslog unix domain socket - default = %s" % default
        self.add_option(
            "--syslog",
            action="store",
            dest="syslog",
            default=default,
            type="unixdomainsocket",
            help=help)

        default = None
        help = "log to this file - default = %s" % default
        self.add_option(
            "--logfile",
            action="store",
            dest="logging_file",
            default=default,
            type="string",
            help=help)
