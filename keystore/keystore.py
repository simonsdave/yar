#!/usr/bin/env python
#-------------------------------------------------------------------------------
#
# keystore.py
#
#-------------------------------------------------------------------------------

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
	if httplib.CREATED == response.status:
		print "Successfully created database '%s' on '%s:%d'." % (
			db, host, port)
	else:
		print "Failed to create database '%s' on '%s:%d'." % (
			db, host, port)

	design_doc = None
	with open("keystore.json", "r") as f:
		design_doc = f.read()
	print design_doc

	http_client = httplib2.Http()
	response, content = http_client.request(url,"PUT")
	if httplib.CREATED == response.status:
		print "Successfully created database '%s' on '%s:%d'." % (
			db, host, port)
	else:
		print "Failed to create database '%s' on '%s:%d'." % (
			db, host, port)

# headers={"Content-Type": "application/json; charset=utf8"}
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
	print __file__
	# delete()
	# create()

#------------------------------------------------------------------- End-of-File
