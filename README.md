This repo is the result of being convinced that it wouldn't be that
hard to write an API Management solution. Why? Because it felt like so much
componentry already existed in the open source community. All that should be necessary
was assembling this pre-existing componentry into a solution and
providing a suite of automated tests to validate the solution's correctness. 

See the [Wiki](https://github.com/simonsdave/yar/wiki) for a more complete description and discussion of yar.

Prerequisites 
-------------
* code written and tested on Mac OS X 10.8.4 using:
  * [Python 2.7.2](http://www.python.org/)
  * [virtualenv 1.9.1](https://pypi.python.org/pypi/virtualenv)
  * [CouchDB 1.2 & 1.3](http://couchdb.apache.org/)
  * [memcached 1.4.13](http://memcached.org/)
  * [command line tools (OS X Mountain Lion) for Xcode - April 2013](https://developer.apple.com/downloads/index.action)
* see
[requirements.txt](https://github.com/simonsdave/yar/blob/master/requirements.txt "requirements.txt")
for the complete list of python packages on which yar depends

Development
-----------
The following (brief) instructions describe how to setup a yar development environment and
issue your first request through the infrastructure.
The commands below are expected to be executed in your
favorite terminal emulator ([iTerm2](http://www.iterm2.com/) happens to be my favorite).
In the instructions below it's assumed yar is installed to your home directory.

> Before you start working through the instructions below make sure you
> have installed the components described above. In particular, if you don't install
> [command line tools (OS X Mountain Lion) for Xcode - April 2013](https://developer.apple.com/downloads/index.action)
> you'll find it hard to debug the error messages produced by **source bin/cfg4dev**. 

* get the source code by running the following in a new terminal window

~~~~~
cd; git clone https://github.com/simonsdave/yar.git
~~~~~

* start the App Server with the following in a new terminal window - by default the app
server listens on port 8080 - this app server is only for testing/development - you wouldn't
use this in a production deployment:

~~~~~
cd; cd yar; source bin/cfg4dev; app_server --log=info
~~~~~

* start the Key Store - if CouchDB isn't already running, in a new terminal window start CouchDB
using the following command - by default CouchDB listens on port 5984

~~~~~
couchdb
~~~~~

* configure the Key Store: assuming you don't already have a creds database on your CouchDB configure Key Store
by running the following in a new terminal window

~~~~~
cd; cd yar; source bin/cfg4dev; key_store_installer --log=info --create=true
~~~~~

* start the Key Server: in a new terminal window run the following to start the Key Server - by
default the Key Server will listen on port 8070

~~~~~
cd; cd yar; source bin/cfg4dev; key_server --log=info
~~~~~

* generate an inital set of credentials by issuing the
follow [cURL](http://en.wikipedia.org/wiki/CURL) request:

~~~~~
curl \
  -v \
  -X POST \
  -H "Content-Type: application/json; charset=utf8" \
  -d "{\"owner\":\"simonsdave@gmail.com\"}" \
  http://localhost:8070/v1.0/creds
~~~~~

* using the credentials returned by the above [cURL](http://en.wikipedia.org/wiki/CURL)
request, create a new file called ~/.yar.creds
in the following format (this file will be used in a bit by
[yarcurl](https://github.com/simonsdave/yar/wiki/Utilities#yarcurl)):

~~~~~
MAC_KEY_IDENTIFIER=35c3913e63ce451d9f58fed1125a2594
MAC_KEY=d9c_PQf58YF-c30TrfBsgY_lMRirNg93qgKBkMN2Fak
MAC_ALGORITHM=hmac-sha-1
~~~~~

* start the Nonce Store: if memcached isn't already running, in a new terminal window start memcached using
the following command - by default memcached listens on port 11211

~~~~~
memcached -vv
~~~~~

* start the Authentication Server by running the following in a new terminal window - by
default, the Autentication Server listens on port 8000

~~~~~
cd; cd yar; source bin/cfg4dev; auth_server --log=info
~~~~~

* Okay, all of your infrastructure should now be running!
Time to issue your first request to the app server thru the authentication server.
In a new terminal window issue the following commands to setup your PATH:

~~~~~
cd; cd yar; source bin/cfg4dev
~~~~~

* In the same window that you executed the above commands, you'll now use
[yarcurl](https://github.com/simonsdave/yar/wiki/Utilities#yarcurl) 
to issue a request to the app server via the auth server:

~~~~~
yarcurl GET http://localhost:8000/dave-was-here.html
~~~~~

