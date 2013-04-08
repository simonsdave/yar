#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# keystore.py
#
#-------------------------------------------------------------------------------

import os
import sys
import glob
import httplib
import httplib2

#-------------------------------------------------------------------------------

default_host = "localhost"
default_port = 5984
default_db = "macaa"

#-------------------------------------------------------------------------------

def create(db=default_db,host=default_host,port=default_port):

	url = "http://%s:%d/%s" % (host, port, db)
	http_client = httplib2.Http()
	response, content = http_client.request(url,"PUT")
	if httplib.CREATED != response.status:
		print "Failed to create database '%s' on '%s:%d'." % (db, host, port)
		return False
	print "Successfully created database '%s' on '%s:%d'." % (db, host, port)

	path = os.path.split(sys.argv[0])[0]
	design_doc_file_name_pattern = os.path.join(path,"*.json")
	for design_doc_file_name in glob.glob(design_doc_file_name_pattern):

		design_doc_name = os.path.basename(design_doc_file_name)[:-len(".json")]

		with open(design_doc_file_name, "r") as design_doc_file:
			design_doc = design_doc_file.read()

		url = "http://%s:%d/%s/_design/%s" % (host, port, db, design_doc_name)
		http_client = httplib2.Http()
		response, content = http_client.request(
			url,
			"PUT",
			body=design_doc,
			headers={"Content-Type": "application/json; charset=utf8"})
		if httplib.CREATED != response.status:
			print "Failed to create design doc '%s'" % url
			return False
		print "Successfully created design doc '%s'" % url

	return True

#-------------------------------------------------------------------------------

def delete(db=default_db,host=default_host,port=default_port):

	url = "http://%s:%d/%s" % (host, port, db)
	http_client = httplib2.Http()
	response, content = http_client.request(url,"DELETE")
	if httplib.OK == response.status:
		print "Successfully deleted database '%s' on '%s:%d'." % (
			db, host, port)
	else:
		print "Failed to delete database '%s' on '%s:%d'." % (
			db, host, port)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
	delete()
	create()

#------------------------------------------------------------------- End-of-File
