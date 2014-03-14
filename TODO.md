To Do's
-------

General
-------
* rename CouchDB to couchdb - need to change create_images.sh

CouchDB Installer
-----------------
* configure
[Automatic_Compaction](https://wiki.apache.org/couchdb/Compaction#Automatic_Compaction)
of databases and views
* write Python script to config cont replication between master & its backup
* write Python script to config cont replication between master & its backup

Auth Server
-----------
* performance improvement - basic authentication - cache hashed api
key in memcached for time limit of ?1? minute to reduce overhead
of always going out to key server
* configure request routing and load balancing to app servers
and key servers using HAProxy
  * [How can I make haproxy route requests based on URL substrings?](http://serverfault.com/questions/306968/how-can-i-make-haproxy-route-requests-based-on-url-substrings)
  * [HAProxy Configuration Manual - Using ACLs](http://haproxy.1wt.eu/download/1.3/doc/configuration.txt)
~~~~~
backend be1 # this is your default backend
  ...
backend be2 # this is for /tag-02 requests
  ...

frontend fe
  ...
  default_backend be1
  acl url_tag02 path_beg /tag-02
  use_backend be2 if url_tag02
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
