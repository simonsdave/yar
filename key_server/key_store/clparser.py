"""This module contains all the logic required to parse the key
store installer's command line."""

#-------------------------------------------------------------------------------

import logging
import optparse

import clparserutil

#-------------------------------------------------------------------------------

class CommandLineParser(optparse.OptionParser):

	def __init__(self):
		optparse.OptionParser.__init__(
			self,
			"usage: %prog [options]",
			option_class=clparserutil.Option)

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
			help="where's CouchDB running - default = localhost:5984" )

		self.add_option(
			"--database",
			action="store",
			dest="database",
			default="creds",
			help="database - default = creds" )

		self.add_option(
			"--delete",
			action="store",
			dest="delete",
			default=False,
			type="boolean",
			help="delete before creating key store - default = False" )

		self.add_option(
			"--create",
			action="store",
			dest="create",
			default=True,
			type="boolean",
			help="create key store - default = True" )

#------------------------------------------------------------------- End-of-File
