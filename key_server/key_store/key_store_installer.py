#!/usr/bin/env python
"""This module contains all the logic required to create and delete
a CouchDB database that implements key store."""

#-------------------------------------------------------------------------------

import logging
import os
import sys
import glob
import httplib
import httplib2

from command_line_parser import CommandLineParser

#-------------------------------------------------------------------------------

_logger = logging.getLogger("KEYSTORE_%s" % __name__)

#-------------------------------------------------------------------------------

def _is_couchdb_accessible(host="localhost:5984"):
	"""Returns True if there's a CouchDB server running on ```host```.
	Otherwise returns False. ```host``` is expected to be of the form
	host:port."""

	url = "http://%s" % host
	http_client = httplib2.Http()
	try:
		response, content = http_client.request(url,"GET")
	except:
		return False
	return httplib.OK == response.status

#-------------------------------------------------------------------------------

def create(database="macaa", host="localhost:5984"):

	_logger.info("Creating database '%s' on '%s'", database, host)

	#
	# first create the database
	#
	url = "http://%s/%s" % (host, database)
	http_client = httplib2.Http()
	response, content = http_client.request(url,"PUT")
	if httplib.CREATED != response.status:
		_logger.error("Failed to create database '%s' on '%s'", database, host)
		return False
	_logger.info("Successfully created database '%s' on '%s'", database, host)

	#
	# now iterate thru each file in the same directory as this script
	# for files that end with ".json" - these files are assumed to be
	# design documents with the filename (less ".json" being the design
	# document name
	#
	path = os.path.split(__file__)[0]
	design_doc_file_name_pattern = os.path.join(path,"*.json")
	for design_doc_file_name in glob.glob(design_doc_file_name_pattern):

		_logger.info(
			"Creating design doc '%s' in database '%s' on '%s'",
			design_doc_file_name,
			database,
			host)

		design_doc_name = os.path.basename(design_doc_file_name)[:-len(".json")]

		with open(design_doc_file_name, "r") as design_doc_file:
			design_doc = design_doc_file.read()

		url = "http://%s/%s/_design/%s" % (host, database, design_doc_name)
		http_client = httplib2.Http()
		response, content = http_client.request(
			url,
			"PUT",
			body=design_doc,
			headers={"Content-Type": "application/json; charset=utf8"})
		if httplib.CREATED != response.status:
			_logger.error("Failed to create design doc '%s'", url)
			return False
		_logger.info("Successfully created design doc '%s'", url)

	return True

#-------------------------------------------------------------------------------

def delete(database="macaa", host="localhost:5984"):

	_logger.info("Deleting database '%s' on '%s'", database, host)
	url = "http://%s/%s" % (host, database)
	http_client = httplib2.Http()
	response, content = http_client.request(url,"DELETE")
	if httplib.OK != response.status:
		_logger.error("Failed to delete database '%s' on '%s'", database, host)
		return False
	_logger.info("Successfully deleted database '%s' on '%s'", database, host)
	return True

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	clp = CommandLineParser()
	(clo, cla) = clp.parse_args()

	loggingLevel = getattr(logging, clo.loggingLevel)
	logging.basicConfig(level=loggingLevel)

	if not _is_couchdb_accessible(clo.host):
		_logger.error("CouchDB isn't running on '%s'", clo.host)
		sys.exit(1)

	if clo.delete:
		if not delete(clo.database,clo.host):
			sys.exit(1)

	if clo.create:
		if not create(clo.database,clo.host):
			sys.exit(1)

	sys.exit(0)

#------------------------------------------------------------------- End-of-File
