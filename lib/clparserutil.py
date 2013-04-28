"""This module contains a series of generally useful and reusable
components for use when building extensions to the optparse module
which parses command lines."""

#-------------------------------------------------------------------------------

import re
import logging
import optparse

#-------------------------------------------------------------------------------

def check_logging_level(option, opt, value):
	"""Type checking function for command line parser's 'logginglevel' type."""
	if re.match("^(DEBUG|INFO|WARNING|ERROR|CRITICAL|FATAL)$", value):
		return getattr(logging, value)
	msg = "option %s: should be one of DEBUG, INFO, WARNING, ERROR, CRITICAL or FATAL" % opt
	raise optparse.OptionValueError(msg)

#-------------------------------------------------------------------------------

def check_host_colon_port(option, opt, value):
	"""Type checking function for command line parser's 'hostcolonport' type."""
	reg_ex = re.compile("^[^\s]+\:\d+$")
	if reg_ex.match(value):
		return value
	msg = "option %s: should be host:port format" % opt
	raise optparse.OptionValueError(msg)

#-------------------------------------------------------------------------------

def _check_boolean(option, opt, value):
	"""Type checking function for command line parser's 'boolean' type."""
	true_reg_ex = re.compile("^(true|t|y|yes|1)$", re.IGNORECASE)
	if true_reg_ex.match(value):
		return True
	false_reg_ex = re.compile("^(false|f|n|no|0)$", re.IGNORECASE)
	if false_reg_ex.match(value):
		return False
	msg = "option %s: should be one of true, false, yes, no, 1 or 0" % opt
	raise optparse.OptionValueError(msg)

#-------------------------------------------------------------------------------

class Option(optparse.Option):
    """Adds hostcolonport, boolean & logginglevel types to the command
	line parser's list of available types."""
    TYPES = optparse.Option.TYPES + ("hostcolonport", "logginglevel", "boolean", )
    TYPE_CHECKER = optparse.Option.TYPE_CHECKER.copy()
    TYPE_CHECKER["hostcolontport"] = check_host_colon_port
    TYPE_CHECKER["logginglevel"] = check_logging_level
    TYPE_CHECKER["boolean"] = _check_boolean

#------------------------------------------------------------------- End-of-File
