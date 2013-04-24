"""This module contains all the logic required to parse the app
server's command line."""

#-------------------------------------------------------------------------------

import re
import logging
import optparse

#-------------------------------------------------------------------------------

def _check_logging_level(option, opt, value):
	"""Type checking function for command line parser's 'logginglevel' type."""
	if re.match("^(DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL)$", value):
		return getattr(logging, value)
	msg = "option %s: should be one of DEBUG, INFO, WARNING, ERROR, CRITICAL or FATAL" % opt
	raise optparse.OptionValueError(msg)

#-------------------------------------------------------------------------------

class _Option(optparse.Option):
	"""Adds logging_level types to the command line parser's
	list of available types."""
	TYPES = optparse.Option.TYPES + ("logginglevel",)
	TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
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
			"--port",
			action="store",
			dest="port",
			default=8080,
			type=int,
			help="port" )

#------------------------------------------------------------------- End-of-File
