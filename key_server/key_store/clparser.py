"""This module contains all the logic required to parse the key
store installer's command line."""

#-------------------------------------------------------------------------------

import re
import logging
import optparse

#-------------------------------------------------------------------------------

def _check_host_colon_port(option, opt, value):
	"""Type checking function for command line parser's 'hostcolonport' type."""
	reg_ex = re.compile("^[^\s]+\:\d+$")
	if reg_ex.match(value):
		return value
	msg = "option %s: should be host:port format" % opt
	raise optparse.OptionValueError(msg)

#-------------------------------------------------------------------------------

def _check_logging_level(option, opt, value):
	"""Type checking function for command line parser's 'logginglevel' type."""
	if re.match("^(DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL)$", value):
		return getattr(logging, value)
	msg = "option %s: should be one of DEBUG, INFO, WARNING, ERROR, CRITICAL or FATAL" % opt
	raise optparse.OptionValueError(msg)

#-------------------------------------------------------------------------------

class _Option(optparse.Option):
	"""Adds key_store and hostcolonport types to the command line parser's
	list of available types."""
	TYPES = optparse.Option.TYPES + ("hostcolonport","logginglevel",)
	TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
	TYPE_CHECKER["hostcolontport"] = _check_host_colon_port
	TYPE_CHECKER["logginglevel"] = _check_logging_level

#-------------------------------------------------------------------------------

class CommandLineParser(optparse.OptionParser):

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
			"--host",
			action="store",
			dest="host",
			default="localhost:5984",
			type="hostcolonport",
			help="CouchDB install" )

		self.add_option(
			"--database",
			action="store",
			dest="database",
			default="macaa",
			help="database" )

		self.add_option(
			"--delete",
			action="store_true",
			dest="delete",
			default=False,
			help="delete before creating" )

		self.add_option(
			"--create",
			action="store_true",
			dest="create",
			default=True,
			help="delete before creating" )

#------------------------------------------------------------------- End-of-File
