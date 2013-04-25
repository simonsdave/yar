"""Super simple module that's only purpose in life is to install a
SIGINT handler so that when an app is halted using a CTRL+C it looks
like a clean shutdown."""

import signal
import sys

#-------------------------------------------------------------------------------

def _term_signal_handler(signalNumber, frame):
	assert signalNumber == signal.SIGINT
	sys.exit(0)

#-------------------------------------------------------------------------------

def install_handler():
	"""Install this module's SIGTERM handler."""
	signal.signal(signal.SIGINT, _term_signal_handler)

#------------------------------------------------------------------- End-of-File
