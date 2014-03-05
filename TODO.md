To Do's
-------

CouchDB Installer
-----------------
* configure
[Automatic_Compaction](https://wiki.apache.org/couchdb/Compaction#Automatic_Compaction)
of databases and views
* Python script to config cont replication between two key servers

Auth Server
-----------
* performance improvement - basic authentication - cache hashed api
key in memcached for time limit of ?1? minute to reduce overhead
of always going out to key server

Documentation
-------------
* describe how key store doesn't need to worry about merge conflicts

Utilities
---------
* yarcurl isn't working on Mac OS X now after it was "fixed"
to work on Ubuntu; error messages
~~~~~
/Users/dave.simons/yar/bin/yarcurl: line 109: $NRS: ambiguous redirect
/Users/dave.simons/yar/bin/yarcurl: line 117: $NRS: ambiguous redirect
~~~~~

Integration Testing
-------------------
* plot of # of keys vs db size

Authorization
-------------
* key concepts
  * authentication
  * authorization
  * accounting
* initial capabilities not in scope
  * groups of principles
  * explicitly denying access (what's the name of this?) - once this is
supported we'll represent it by an empty array of http_methods
in the /authorizations resource 
* authorization store
* *principle* is authorized to access any resource that starts with *url*; when
the auth server has successfully authenticated a request it sends a request to
the authorization store to get all authorizations for *principle*  resources that 
~~~~~
/authorizations/{id}
{
	"url": ...,
	"principle": ...,
	"http_methods": [..., ..., ...]
}
~~~~~
