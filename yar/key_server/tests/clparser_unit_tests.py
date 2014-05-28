"""This module implements a collection of unit tests for
the Key Server's key_server.clparser.CommandLineParser."""

import logging
import unittest

from yar.key_server.clparser import CommandLineParser


class CommandLineParserUnitTase(unittest.TestCase):
    """A collection of unit tests for the Key Server's
    key_server.clparser.CommandLineParser."""

    def test_defaults(self):
        """Verify the command line parser supplies the
        expected defaults when not command line arguments
        are supplied."""
        args = []

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8070))
        self.assertEqual(clo.key_store, "127.0.0.1:5984/creds")
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
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8070))
        self.assertEqual(clo.key_store, "127.0.0.1:5984/creds")
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
        self.assertEqual(clo.key_store, "127.0.0.1:5984/creds")
        self.assertIsNone(clo.logging_file)
        self.assertIsNone(clo.syslog)

    def test_key_store(self):
        """Verify the command line parser correctly parses
        the --key_store command line arg."""
        args = [
            "--key_store", "1.1.1.1:7878/bindle",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8070))
        self.assertEqual(clo.key_store, args[-1])
        self.assertIsNone(clo.logging_file)
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
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8070))
        self.assertEqual(clo.key_store, "127.0.0.1:5984/creds")
        self.assertIsNone(clo.logging_file)
        self.assertEqual(clo.syslog, args[-1])

    def test_logging_file(self):
        """Verify the command line parser correctly parses
        the --logfile command line arg."""
        args = [
            "--logfile", "/dave/was/here.log",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8070))
        self.assertEqual(clo.key_store, "127.0.0.1:5984/creds")
        self.assertEqual(clo.logging_file, args[-1])
        self.assertIsNone(clo.syslog)
