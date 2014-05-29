"""This module implements a collection of unit tests for
the App Service's app_service.clparser.CommandLineParser."""

import logging
import unittest

from yar.app_service.clparser import CommandLineParser


class CommandLineParserUnitTase(unittest.TestCase):
    """A collection of unit tests for the Key Service's
    key_service.clparser.CommandLineParser."""

    def test_defaults(self):
        """Verify the command line parser supplies the
        expected defaults when not command line arguments
        are supplied."""
        args = []

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8080))
        self.assertIsNone(clo.syslog)
        self.assertIsNone(clo.logging_file)

    def test_logging_level(self):
        """Verify the command line parser correctly parses
        the --log command line arg."""
        args = [
            "--log", "info",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.INFO)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8080))
        self.assertIsNone(clo.syslog)
        self.assertIsNone(clo.logging_file)

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
        self.assertIsNone(clo.syslog)
        self.assertIsNone(clo.logging_file)

    def test_syslog(self):
        """Verify the command line parser correctly parses
        the --syslog command line arg."""
        args = [
            "--syslog", "/dave/was/here",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8080))
        self.assertEqual(clo.syslog, args[-1])
        self.assertIsNone(clo.logging_file)

    def test_logging_file(self):
        """Verify the command line parser correctly parses
        the --logfile command line arg."""
        args = [
            "--logfile", "/dave/was/here.log",
        ]

        clp = CommandLineParser()
        (clo, cla) = clp.parse_args(args)

        self.assertEqual(clo.logging_level, logging.ERROR)
        self.assertEqual(clo.listen_on, ("127.0.0.1", 8080))
        self.assertIsNone(clo.syslog)
        self.assertEqual(clo.logging_file, args[-1])
