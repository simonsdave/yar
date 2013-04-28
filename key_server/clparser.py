"""This module contains all the logic required to parse the key
server's command line."""

import optparse
import re
import logging

import clparserutil

#-------------------------------------------------------------------------------

def _check_key_store(option, opt, value):
	"""Type checking function for command line parser's 'key_store' type."""
	if re.match("^[^\s]+\:\d+\/[^\s]+$", value):
		return value
	msg = "option %s: required format is host:port/database" % opt
	raise optparse.OptionValueError(msg)

#-------------------------------------------------------------------------------

class _Option(optparse.Option):
	"""Adds key_store and logginglevel types to the command line parser's
	list of available types."""
	TYPES = optparse.Option.TYPES + ("key_store","logginglevel",)
	TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
	TYPE_CHECKER["key_store"] = _check_key_store
	TYPE_CHECKER["logginglevel"] = clparserutil.check_logging_level

#-------------------------------------------------------------------------------

class CommandLineParser(optparse.OptionParser):
	"""This class parses the key server's command line."""

	def __init__(self):
		optparse.OptionParser.__init__(
			self,
			"usage: %prog [options]",
			option_class=_Option)

		self.add_option(
			"--log",
			action="store",
			dest="logging_level",
			default=logging.ERROR,
			type="logginglevel",
			help="logging level [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL] - default = ERRROR" )

		self.add_option(
			"--port",
			action="store",
			dest="port",
			default=8070,
			type=int,
			help="port - default = 8070" )

		self.add_option(
			"--key_store",
			action="store",
			dest="key_store",
			default="localhost:5984/macaa",
			type="key_store",
			help="key store - host:port/database - default = localhost:5984/macaa" )

#------------------------------------------------------------------- End-of-File
