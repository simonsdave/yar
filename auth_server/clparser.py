"""This module contains all the logic required to parse the authentication
server's command line."""

import optparse
import re
import logging

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
	reg_ex = re.compile("^(DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL)$")
	if reg_ex.match(value):
		logging_level = getattr(logging, value)
		return logging_level
	msg = "option %s: should be one of DEBUG, INFO, WARNING, ERROR, CRITICAL or FATAL" % opt
	raise optparse.OptionValueError(msg)

#-------------------------------------------------------------------------------

class _Option(optparse.Option):
	"""Adds hostcolonport and logginglevel types to the command line parser's
	list of available types."""
	TYPES = optparse.Option.TYPES + ("hostcolonport","logginglevel",)
	TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
	TYPE_CHECKER["hostcolonport"] = _check_host_colon_port
	TYPE_CHECKER["logginglevel"] = _check_logging_level

#-------------------------------------------------------------------------------

class CommandLineParser(optparse.OptionParser):
	"""This class parses the auth server's command line."""

	def __init__(self):
		optparse.OptionParser.__init__(
			self,
			"usage: %prog [options]",
			option_class=_Option)

		self.add_option(
			"--logback",
			action="store",
			choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL","FATAL"],
			dest="loggingLevel",
			default="ERROR",
			help="logging level [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL] - default = ERRROR" )

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
			default="8000",
			type=int,
			help="database" )

		self.add_option(
			"--keyserver",
			action="store",
			dest="key_server",
			default="localhost:6969",
			type="hostcolonport",
			help="key server - host:port" )

		self.add_option(
			"--appserver",
			action="store",
			dest="app_server",
			default="localhost:8080",
			type="hostcolonport",
			help="app server - host:port" )

#------------------------------------------------------------------- End-of-File
