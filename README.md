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
To start the authorization server:
~~~~~
./auth_server.py --port=8000 --key_server=localhost:6969 --app_server=localhost:8080
~~~~~
To make a request to the app server thru the authentication server:
~~~~~
curl \
  -v \
  -X GET \
  -H "Authorization: MAC id=\"h480djs93hd8\", ts=\"00000\", nonce=\"264095:dj83hs9s\", ext=\"davsim\", mac=\"SLDJd4mg43cjQfElUs3Qub4L6xE=\"" \
  http://localhost:8000/dave.html
~~~~~

Key Server 
----------
To start the key server:
~~~~~
./key_server.py --port=6969 --key_store=localhost:5984/creds
~~~~~
By default the key server will attempt to listen on port 8070 and connect a key store at localhost:5984/creds.

To get all MAC credentials currently saved in the key store:
~~~~~~
curl -s -X GET http://localhost:6969/v1.0/mac_creds
~~~~~~
All MAC credentials are "owned" by someone.
An owner's identity is represented below as an opaque string at least one character long.
To create a set of credentials:
~~~~~~
curl \
  -v \
  -X POST \
  -H "Content-Type: application/json; charset=utf8" \
  -d "{\"owner\":\"simonsdave@gmail.com\"}" \
  http://localhost:6969/v1.0/mac_creds
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
In the examples below, CouchDB is assumed to be running on localhost and listening on port 5984.
To create the key store:
~~~~~
./key_store_installer.py --host=localhost:5984 --database=creds --log=INFO --delete
~~~~~
To get all MAC credentials currently saved in the key store:
~~~~~~
curl -s -X GET http://localhost:5984/creds/_design/creds/_view/all
~~~~~~
To get an existing set of creditials:
~~~~~
curl -s -X GET http://localhost:5984/creds/<MAC key identifier>
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
* Authentication
 * [HTTP Authentication: MAC Access Authentication - note this is version 2 from 28 Nov '12](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02")
 * [OAuth 2.0](http://oauth.net/2/ "OAuth 2.0")
 * [macauthlib 0.5.0](https://github.com/mozilla-services/macauthlib) (pip install macauthlib)
* Tokenization
 * [JSONPath](http://goessner.net/articles/JsonPath/)
 * [Cybersource: Payment Tokenization - Using the Simple Order API](http://apps.cybersource.com/library/documentation/dev_guides/Payment_Tokenization/SO_API/Payment_Tokenization_SO_API.pdf)
* Technology
 * [couchdb-python](http://code.google.com/p/couchdb-python/)
 * [6 Feb '11: using Tornado as a proxy](https://groups.google.com/forum/?fromgroups=#!topic/python-tornado/TB_6oKBmdlA)

Demo Story
----------
~~~~~
>git clone https://github.com/simonsdave/apimgmt.git
Cloning into 'apimgmt'...
remote: Counting objects: 702, done.
remote: Compressing objects: 100% (345/345), done.
remote: Total 702 (delta 439), reused 604 (delta 344)
Receiving objects: 100% (702/702), 110.95 KiB, done.
Resolving deltas: 100% (439/439), done.
>cd apimgmt
>dir
total 16
-rw-r--r--  1 dave  staff  3541 Apr 28 08:55 README.md
drwxr-xr-x  4 dave  staff   136 Apr 28 08:55 app_server
drwxr-xr-x  8 dave  staff   272 Apr 28 08:55 auth_server
drwxr-xr-x  4 dave  staff   136 Apr 28 08:55 bin
drwxr-xr-x  6 dave  staff   204 Apr 28 08:55 key_server
drwxr-xr-x  7 dave  staff   238 Apr 28 08:55 lib
-rw-r--r--  1 dave  staff    47 Apr 28 08:55 requirements.txt
>source bin/cfg4dev
New python executable in env/bin/python
Installing setuptools............done.
Installing pip...............done.
Downloading/unpacking httplib2==0.8 (from -r /Users/dave/apimgmt/requirements.txt (line 1))
  Downloading httplib2-0.8.tar.gz (110kB): 110kB downloaded
  Running setup.py egg_info for package httplib2

Downloading/unpacking jsonschema==1.3.0 (from -r /Users/dave/apimgmt/requirements.txt (line 2))
  Downloading jsonschema-1.3.0.zip (57kB): 57kB downloaded
  Running setup.py egg_info for package jsonschema

Downloading/unpacking tornado==2.4.1 (from -r /Users/dave/apimgmt/requirements.txt (line 3))
  Downloading tornado-2.4.1.tar.gz (348kB): 348kB downloaded
  Running setup.py egg_info for package tornado

    warning: no previously-included files matching '_auto2to3*' found anywhere in distribution
Installing collected packages: httplib2, jsonschema, tornado
  Running setup.py install for httplib2

  Running setup.py install for jsonschema

  Running setup.py install for tornado

    warning: no previously-included files matching '_auto2to3*' found anywhere in distribution
Successfully installed httplib2 jsonschema tornado
Cleaning up...
(env)>more requirements.txt
httplib2==0.8
jsonschema==1.3.0
tornado==2.4.1

(env)>cd key_server/key_store
(env)>dir
total 48
-rw-r--r--  1 dave  staff     0 Apr 28 08:55 __init__.py
-rw-r--r--  1 dave  staff   139 Apr 28 11:32 __init__.pyc
-rw-r--r--  1 dave  staff  1384 Apr 28 10:34 clparser.py
-rw-r--r--  1 dave  staff  1616 Apr 28 11:13 clparser.pyc
-rw-r--r--  1 dave  staff   302 Apr 28 08:55 creds.json
-rwxr-xr-x  1 dave  staff  3742 Apr 28 11:14 key_store_installer.py
-rw-r--r--  1 dave  staff  3491 Apr 28 11:32 key_store_installer.pyc

(env)>/key_store_installer.py --help
Usage: key_store_installer.py [options]

Options:
  -h, --help           show this help message and exit
  --log=LOGGING_LEVEL  logging level [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL]
                       - default = ERRROR
  --host=HOST          CouchDB install
  --database=DATABASE  database
  --delete=DELETE      delete before creating key store - default = False
  --create=CREATE      create key store - default = True
  
(env)>./key_store_installer.py --log=INFO --delete=true
CRITICAL:KEYSTORE___main__:CouchDB isn't running on 'localhost:5984'

(env)couchdb
Apache CouchDB 1.2.1 (LogLevel=info) is starting.
Apache CouchDB has started. Time to relax.
[info] [<0.31.0>] Apache CouchDB has started on http://127.0.0.1:5984/

(env)>./key_store_installer.py --log=INFO --delete=true
INFO:KEYSTORE___main__:Deleting database 'creds' on 'localhost:5984'
INFO:KEYSTORE___main__:Successfully deleted database 'creds' on 'localhost:5984'
INFO:KEYSTORE___main__:Creating database 'creds' on 'localhost:5984'
INFO:KEYSTORE___main__:Successfully created database 'creds' on 'localhost:5984'
INFO:KEYSTORE___main__:Creating design doc './creds.json' in database 'creds' on 'localhost:5984'
INFO:KEYSTORE___main__:Successfully created design doc 'http://localhost:5984/creds/_design/creds'

(env)>(env)>dir
total 80
-rw-r--r--  1 dave  staff   1855 Apr 28 08:55 clparser.py
-rw-r--r--  1 dave  staff   2295 Apr 28 11:32 clparser.pyc
-rwxr-xr-x  1 dave  staff   7602 Apr 28 08:55 key_server.py
-rw-r--r--  1 dave  staff   8785 Apr 28 11:32 key_server.pyc
-rwxr-xr-x  1 dave  staff  11420 Apr 28 08:55 key_server_unit_tests.py
drwxr-xr-x  9 dave  staff    306 Apr 28 11:32 key_store

(env)>(env)>./key_server_unit_tests.py
.................
----------------------------------------------------------------------
Ran 17 tests in 7.904s

OK

(env)>/key_server.py --help
Usage: key_server.py [options]

Options:
  -h, --help            show this help message and exit
  --log=LOGGING_LEVEL   logging level
                        [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL] - default =
                        ERRROR
  --port=PORT           port - default = 8070
  --key_store=KEY_STORE
                        key store - host:port/database

(env)>

~~~~~
