"""This module contains a series of generally useful and reusable
components for use when building extensions to optparse.OptionParser
which parse command lines."""

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

#------------------------------------------------------------------- End-of-File
