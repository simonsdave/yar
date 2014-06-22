"""This module implements a collection of unit tests for
the yar.util.couchdb_installer module."""

import logging
import unittest

from yar.util.couchdb_installer import CommandLineParser


class CommandLineParserUnitTase(unittest.TestCase):
    """A collection of unit tests for the
    yar.util.couchdb_installer module."""

    def test_defaults(self):
        """Verify the command line parser supplies the
        expected defaults when not command line arguments
        are supplied."""
        args = []

        clp = CommandLineParser("description", "creds")
        (clo, cla) = clp.parse_args(args)

        self.assertFalse(clo.delete)
        self.assertTrue(clo.create)
        self.assertTrue(clo.create_design_docs)
        self.assertEqual(clo.database, "creds")
        self.assertEqual(clo.host, "127.0.0.1:5984")
        self.assertEqual(clo.logging_level, logging.ERROR)

    def test_logging_level(self):
        """Verify the command line parser correctly parses
        the --log command line arg."""
        args = [
            "--log", "info",
        ]

        clp = CommandLineParser("description", "creds")
        (clo, cla) = clp.parse_args(args)

        self.assertFalse(clo.delete)
        self.assertTrue(clo.create)
        self.assertTrue(clo.create_design_docs)
        self.assertEqual(clo.database, "creds")
        self.assertEqual(clo.host, "127.0.0.1:5984")
        self.assertEqual(clo.logging_level, logging.INFO)

    def test_host(self):
        """Verify the command line parser correctly parses
        the --host command line arg."""
        args = [
            "--host", "example.com:1234",
        ]

        clp = CommandLineParser("description", "creds")
        (clo, cla) = clp.parse_args(args)

        self.assertFalse(clo.delete)
        self.assertTrue(clo.create)
        self.assertTrue(clo.create_design_docs)
        self.assertEqual(clo.database, "creds")
        self.assertEqual(clo.host, args[-1])
        self.assertEqual(clo.logging_level, logging.ERROR)

    def test_database(self):
        """Verify the command line parser correctly parses
        the --database command line arg."""
        args = [
            "--database", "davewashere",
        ]

        clp = CommandLineParser("description", "creds")
        (clo, cla) = clp.parse_args(args)

        self.assertFalse(clo.delete)
        self.assertTrue(clo.create)
        self.assertTrue(clo.create_design_docs)
        self.assertEqual(clo.database, args[-1])
        self.assertEqual(clo.host, "127.0.0.1:5984")
        self.assertEqual(clo.logging_level, logging.ERROR)

    def test_create(self):
        """Verify the command line parser correctly parses
        the --create command line arg."""
        args = [
            "--create", "f",
        ]

        clp = CommandLineParser("description", "creds")
        (clo, cla) = clp.parse_args(args)

        self.assertFalse(clo.delete)
        self.assertFalse(clo.create)
        self.assertTrue(clo.create_design_docs)
        self.assertEqual(clo.database, "creds")
        self.assertEqual(clo.host, "127.0.0.1:5984")
        self.assertEqual(clo.logging_level, logging.ERROR)

    def test_create_design_docs(self):
        """Verify the command line parser correctly parses
        the --createdesign command line arg."""
        args = [
            "--createdesign", "f",
        ]

        clp = CommandLineParser("description", "creds")
        (clo, cla) = clp.parse_args(args)

        self.assertFalse(clo.delete)
        self.assertTrue(clo.create)
        self.assertFalse(clo.create_design_docs)
        self.assertEqual(clo.database, "creds")
        self.assertEqual(clo.host, "127.0.0.1:5984")
        self.assertEqual(clo.logging_level, logging.ERROR)

    def test_delete(self):
        """Verify the command line parser correctly parses
        the --delete command line arg."""
        args = [
            "--delete", "t",
        ]

        clp = CommandLineParser("description", "creds")
        (clo, cla) = clp.parse_args(args)

        self.assertTrue(clo.delete)
        self.assertTrue(clo.create)
        self.assertTrue(clo.create_design_docs)
        self.assertEqual(clo.database, "creds")
        self.assertEqual(clo.host, "127.0.0.1:5984")
        self.assertEqual(clo.logging_level, logging.ERROR)
