API Management
==============

Some code Dave is using to explore some thoughts on a simple API Management service.

References 
----------
* [HTTP Authentication: MAC Access Authentication](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-00 "HTTP Authentication: MAC Access Authentication")
* [OAuth 2.0](http://oauth.net/2/ "OAuth 2.0")
* [JSONPath](http://goessner.net/articles/JsonPath/)

Prerequisites 
-------------
* [Tornado 2.4.1](http://www.tornadoweb.org/en/branch2.4/ "Tornado 2.4.1")
* [httplib2 0.8](https://code.google.com/p/httplib2/ "httplib2")

Key Server 
----------
* curl -X POST -H "Content-Type: application/json; charset=utf8" -d "{\"owner\":\"dave.simons@points.com\"}" http://localhost:6969/v1.0/mac_creds/
* curl -s -X GET http://localhost:6969/v1.0/mac_creds
* curl -v -X GET http://localhost:6969/v1.0/mac_creds/<MAC key identifier>
* curl -v -X DELETE http://localhost:6969/v1.0/mac_creds/<MAC key identifier>
