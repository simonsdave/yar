#-------------------------------------------------------------------------------
#
# CommandLineParser.py
#
#-------------------------------------------------------------------------------

import optparse

#-------------------------------------------------------------------------------

class CommandLineParser(optparse.OptionParser):

	def __init__(self):
		optparse.OptionParser.__init__(self, "usage: %prog [options]" )

		self.add_option(
			"-l",
			"--log",
			action="store",
			choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL","FATAL"],
			dest="loggingLevel",
			default="ERROR",
			help="logging level [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL] - default = ERRROR" )

		self.add_option(
			"--host",
			action="store",
			dest="host",
			default="localhost:5984",
			help="CouchDB install" )

		self.add_option(
			"--database",
			action="store",
			dest="database",
			default="macaa",
			help="database" )

#------------------------------------------------------------------- End-of-File
