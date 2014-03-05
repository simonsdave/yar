To Do's
-------

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
* Python script to configure continous reflication between two key servers

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
