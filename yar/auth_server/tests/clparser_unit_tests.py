"""This module implements a collection of unit tests for
the Auth Server's auth_server.clparser.CommandLineParser."""

import logging
import unittest

from yar.auth_server.clparser import CommandLineParser


class CommandLineParserUnitTase(unittest.TestCase):
    """A collection of unit tests for the Auth Server's
    auth_server.clparser.CommandLineParser."""

    def test_defaults(self):
        """Verify the command line parser supplies the
        expected defaults when not command line arguments
        are supplied."""
        args = []

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8000))
        self.assertEqual(clo.app_server_auth_method, "YAR")
        self.assertEqual(clo.key_server, "127.0.0.1:8070")
        self.assertEqual(clo.app_server, "127.0.0.1:8080")
        self.assertEqual(clo.maxage, 30)
        self.assertEqual(clo.nonce_store, ["127.0.0.1:11211"])
        self.assertIsNone(clo.logging_file)
        self.assertIsNone(clo.syslog)

    def test_logging_level(self):
        """Verify the command line parser correctly parses
        the --log command line arg."""
        args = [
            "--log", "info",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.INFO)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8000))
        self.assertEqual(clo.app_server_auth_method, "YAR")
        self.assertEqual(clo.key_server, "127.0.0.1:8070")
        self.assertEqual(clo.app_server, "127.0.0.1:8080")
        self.assertEqual(clo.maxage, 30)
        self.assertEqual(clo.nonce_store, ["127.0.0.1:11211"])
        self.assertIsNone(clo.logging_file)
        self.assertIsNone(clo.syslog)

    def test_listen_on(self):
        """Verify the command line parser correctly parses
        the --lon command line arg."""
        args = [
            "--lon", "1.1.1.1:7878",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("1.1.1.1", 7878))
        self.assertEqual(clo.app_server_auth_method, "YAR")
        self.assertEqual(clo.key_server, "127.0.0.1:8070")
        self.assertEqual(clo.app_server, "127.0.0.1:8080")
        self.assertEqual(clo.maxage, 30)
        self.assertEqual(clo.nonce_store, ["127.0.0.1:11211"])
        self.assertIsNone(clo.logging_file)
        self.assertIsNone(clo.syslog)

    def test_app_server_auth_method(self):
        """Verify the command line parser correctly parses
        the --authmethod command line arg."""
        args = [
            "--authmethod", "DAS",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8000))
        self.assertEqual(clo.app_server_auth_method, "DAS")
        self.assertEqual(clo.key_server, "127.0.0.1:8070")
        self.assertEqual(clo.app_server, "127.0.0.1:8080")
        self.assertEqual(clo.maxage, 30)
        self.assertEqual(clo.nonce_store, ["127.0.0.1:11211"])
        self.assertIsNone(clo.logging_file)
        self.assertIsNone(clo.syslog)

    def test_app_server(self):
        """Verify the command line parser correctly parses
        the --authmethod command line arg."""
        args = [
            "--appserver", "1.1.1.1:6666",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8000))
        self.assertEqual(clo.app_server_auth_method, "YAR")
        self.assertEqual(clo.app_server, "1.1.1.1:6666")
        self.assertEqual(clo.key_server, "127.0.0.1:8070")
        self.assertEqual(clo.maxage, 30)
        self.assertEqual(clo.nonce_store, ["127.0.0.1:11211"])
        self.assertIsNone(clo.logging_file)
        self.assertIsNone(clo.syslog)

    def test_maxage(self):
        """Verify the command line parser correctly parses
        the --maxage command line arg."""
        args = [
            "--maxage", "66",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8000))
        self.assertEqual(clo.app_server_auth_method, "YAR")
        self.assertEqual(clo.app_server, "127.0.0.1:8080")
        self.assertEqual(clo.maxage, int(args[-1]))
        self.assertEqual(clo.key_server, "127.0.0.1:8070")
        self.assertEqual(clo.nonce_store, ["127.0.0.1:11211"])
        self.assertIsNone(clo.logging_file)
        self.assertIsNone(clo.syslog)

    def test_key_server(self):
        """Verify the command line parser correctly parses
        the --keyserver command line arg."""
        args = [
            "--keyserver", "1.1.1.1:6666",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8000))
        self.assertEqual(clo.app_server_auth_method, "YAR")
        self.assertEqual(clo.app_server, "127.0.0.1:8080")
        self.assertEqual(clo.maxage, 30)
        self.assertEqual(clo.key_server, args[-1])
        self.assertEqual(clo.nonce_store, ["127.0.0.1:11211"])
        self.assertIsNone(clo.logging_file)
        self.assertIsNone(clo.syslog)

    def test_nonce_store(self):
        """Verify the command line parser correctly parses
        the --noncestore command line arg."""
        args = [
            "--noncestore", "1.1.1.1:6666",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8000))
        self.assertEqual(clo.app_server_auth_method, "YAR")
        self.assertEqual(clo.app_server, "127.0.0.1:8080")
        self.assertEqual(clo.maxage, 30)
        self.assertEqual(clo.key_server, "127.0.0.1:8070")
        self.assertEqual(clo.nonce_store, [args[-1]])
        self.assertIsNone(clo.logging_file)
        self.assertIsNone(clo.syslog)

    def test_logging_file(self):
        """Verify the command line parser correctly parses
        the --logfile command line arg."""
        args = [
            "--logfile", "/dave/was/here.log",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8000))
        self.assertEqual(clo.app_server_auth_method, "YAR")
        self.assertEqual(clo.app_server, "127.0.0.1:8080")
        self.assertEqual(clo.maxage, 30)
        self.assertEqual(clo.key_server, "127.0.0.1:8070")
        self.assertEqual(clo.nonce_store, ["127.0.0.1:11211"])
        self.assertEqual(clo.logging_file, args[-1])
        self.assertIsNone(clo.syslog)

    def test_syslog(self):
        """Verify the command line parser correctly parses
        the --syslog command line arg."""
        args = [
            "--syslog", "/dave/was/here",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8000))
        self.assertEqual(clo.app_server_auth_method, "YAR")
        self.assertEqual(clo.app_server, "127.0.0.1:8080")
        self.assertEqual(clo.maxage, 30)
        self.assertEqual(clo.key_server, "127.0.0.1:8070")
        self.assertEqual(clo.nonce_store, ["127.0.0.1:11211"])
        self.assertIsNone(clo.logging_file)
        self.assertEqual(clo.syslog, args[-1])
