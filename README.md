API Management
==============

Some code Dave is using to explore some thoughts on a simple API Management service.

Prerequisites 
-------------
* [Tornado 2.4.1](http://www.tornadoweb.org/en/branch2.4/ "Tornado 2.4.1")
* [httplib2 0.8](https://code.google.com/p/httplib2/ "httplib2")

Authentication Server
---------------------
* ...

Tokenization Server
-------------------
* ...

Key Server 
----------
* curl -X POST -H "Content-Type: application/json; charset=utf8" -d "{\"owner\":\"dave.simons@points.com\"}" http://localhost:6969/v1.0/mac_creds
* curl -s -X GET http://localhost:6969/v1.0/mac_creds
* curl -v -X GET http://localhost:6969/v1.0/mac_creds/<MAC key identifier>
* curl -v -X DELETE http://localhost:6969/v1.0/mac_creds/<MAC key identifier>

Key Store
---------
* ...

References
----------
* [HTTP Authentication: MAC Access Authentication](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-00 "HTTP Authentication: MAC Access Authentication")
* [OAuth 2.0](http://oauth.net/2/ "OAuth 2.0")
* [JSONPath](http://goessner.net/articles/JsonPath/)
* [Cybersource: Payment Tokenization - Using the Simple Order API](http://apps.cybersource.com/library/documentation/dev_guides/Payment_Tokenization/SO_API/Payment_Tokenization_SO_API.pdf)

Articles
--------
* [6 Feb '11: using Tornado as a proxy](https://groups.google.com/forum/?fromgroups=#!topic/python-tornado/TB_6oKBmdlA)

