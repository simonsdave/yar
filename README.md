API Management
==============

Some code Dave is using to explore some thoughts on a simple API Management service.

Prerequisites 
-------------
* code written and tested on Mac OS X 10.8.2 using Python 2.7.2 and [virtualenv 1.9.1](https://pypi.python.org/pypi/virtualenv)
* [Tornado 2.4.1](http://www.tornadoweb.org/en/branch2.4/ "Tornado 2.4.1") (pip install tornado)
* [httplib2 0.8](https://code.google.com/p/httplib2/ "httplib2") (pip install httplib2)

Authentication Server
---------------------
* ./authenticationserver.py --port=8080 --key_server=localhost:6969 --app_server=localhost:8081

Tokenization Server
-------------------
* ...

Key Server 
----------
To start the key server:
~~~~~
./app_server.py --port=8080
~~~~~
By default the key server will attempt to use port 8080.

To get all MAC credentials currently saved in the key store:
~~~~~~
curl -s -X GET http://localhost:6969/v1.0/mac_creds | ../bin/pp.sh
~~~~~~
All MAC credentials are "owned" by someone.
An owner's identity is represented below as an opaque string at least one character long.
To create a set of credentials:
~~~~~~
curl -X POST -H "Content-Type: application/json; charset=utf8" -d "{\"owner\":\"simonsdave@gmail.com\"}" http://localhost:6969/v1.0/mac_creds
~~~~~~
To get an existing set of creditials:
~~~~~
curl -v -X GET http://localhost:6969/v1.0/mac_creds/<MAC key identifier>
~~~~~
To delete a set of existing credentials:
~~~~~
curl -v -X DELETE http://localhost:6969/v1.0/mac_creds/<MAC key identifier>
~~~~~

Key Store
---------
The key store is implemented as a CouchDB database.
In the examples below, CouchDB is assumed to be running on localhost port 5984.
To create the key store:
~~~~~
./key_store_installer.py --host=localhost:5984 --database=macaa --log=INFO --delete
~~~~~
To get all MAC credentials currently saved in the key store:
~~~~~~
curl -s -X GET http://localhost:5984/macaa/_design/creds/_view/all | ../bin/pp.sh
~~~~~~
To get an existing set of creditials:
~~~~~
curl -s -X GET http://localhost:5984/macaa/<MAC key identifier>
~~~~~

App Server
----------
To start the app server:
~~~~~
./app_server.py --port=8080
~~~~~
By default the app server will attempt to use port 8080.

The app server will respond to HTTP GET, POST, DELETE and PUT requests.
To confirm the app server is working correctly try:
~~~~~
curl -X GET http://localhost:8080/dave.html
~~~~~

References
----------
* [HTTP Authentication: MAC Access Authentication](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-00 "HTTP Authentication: MAC Access Authentication")
* [OAuth 2.0](http://oauth.net/2/ "OAuth 2.0")
* [JSONPath](http://goessner.net/articles/JsonPath/)
* [Cybersource: Payment Tokenization - Using the Simple Order API](http://apps.cybersource.com/library/documentation/dev_guides/Payment_Tokenization/SO_API/Payment_Tokenization_SO_API.pdf)

Articles
--------
* [6 Feb '11: using Tornado as a proxy](https://groups.google.com/forum/?fromgroups=#!topic/python-tornado/TB_6oKBmdlA)

