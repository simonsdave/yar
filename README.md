So you've spent time writing an awesome RESTful API and now you want to secure it.
You'll soon find there are a number of commerical API management solutions available.
What you'll also find is that there's lots of open source components that it feels like
should be pretty easy to stitch together to create your own API Management solution.
It's that last point that motivated this project. How hard could it really be? Well, turned
out to be more work than I originally thought but it wasn't crazy hard.
With about 1,500 lines of Python this project realizes an API Management solution with
the capabilities outlined below.
Is the project complete? No. Yar is still a work in progress. Below you'll find the
list of big/important things that are on the immediate to do list.
See the [Wiki](https://github.com/simonsdave/yar/wiki) for a more complete description and discussion of yar.

  * authentication using
[OAuth 2.0 Message Authentication Code (MAC) Tokens](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02)
and [Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)
  * key generation for both the above authentication schemes
  * [Keyczar](http://www.keyczar.org/) used for both key generation and HMAC verification
  * [Auth Server](https://github.com/simonsdave/yar/wiki/Auth-Server) and [Key Server](https://github.com/simonsdave/yar/wiki/Key-Server) are [Tornado](http://www.tornadoweb.org/en/stable/) servers leveraging Tornado's [asynchronous](http://www.tornadoweb.org/en/stable/networking.html) for high concurrency operation
  * [Key Store](https://github.com/simonsdave/yar/wiki/Key-Store) is built on [CouchDB](http://couchdb.apache.org/) so the [Key Store](https://github.com/simonsdave/yar/wiki/Key-Store) inherits all the nice architectual/operational qualities of [CouchDB](http://couchdb.apache.org/)
  * intended deployment environment is [Ubuntu 12.04](http://releases.ubuntu.com/12.04.4/) and
development environment is [Mac OS X](http://www.apple.com/ca/osx/)
  
Bigger/important things on the immediate to do list:

  * automated load/stress tests - currently working on this (see [this](https://github.com/simonsdave/yar/tree/master/integration_tests)) while learning how to best leverage [Vagrant](http://www.vagrantup.com/) and [Docker](https://www.docker.io/)
  * securing keys in [Key Store](https://github.com/simonsdave/yar/wiki/Key-Store)
  * authorization service
  * bunch more documentation

Development Prerequisites 
-------------------------
* code written and tested on Mac OS X 10.8.4 using:
  * [Python 2.7.2](http://www.python.org/)
  * [virtualenv 1.9.1](https://pypi.python.org/pypi/virtualenv)
  * [CouchDB 1.2 & 1.3](http://couchdb.apache.org/)
  * [memcached 1.4.13](http://memcached.org/)
  * [command line tools for Xcode](https://developer.apple.com/downloads/index.action)
* see
[requirements.txt](https://github.com/simonsdave/yar/blob/master/requirements.txt "requirements.txt")
for the complete list of python packages on which yar depends

Development Quick Start
-----------------------
The following instructions describe how to setup a yar development environment and
issue your first request through the infrastructure.
The commands below are expected to be executed in your
favorite terminal emulator ([iTerm2](http://www.iterm2.com/) happens to be my favorite).
In the instructions below it's assumed yar is installed to your home directory.

> Before you start working through the instructions below make sure you
> have installed the components described above. In particular, if you don't install
> [command line tools for Xcode](https://developer.apple.com/downloads/index.action)
> you'll find it hard to debug the error messages produced by **source bin/cfg4dev**. 

* get the source code by running the following in a new terminal window

~~~~~
cd; git clone https://github.com/simonsdave/yar.git
~~~~~

* start the App Server with the following in a new terminal window - by default the app
server listens on 127:0.0.1:8080 - this app server is only for
testing/development - you wouldn't use this in a production deployment:

~~~~~
cd; cd yar; source bin/cfg4dev; app_server --log=info
~~~~~

* start the Key Store - if [CouchDB](http://couchdb.apache.org/)
isn't already running, in a new terminal, window start
[CouchDB](http://couchdb.apache.org/)
using the following command - by default [CouchDB](http://couchdb.apache.org/)
listens on 127.0.0.1:5984

~~~~~
couchdb
~~~~~

* configure the Key Store: assuming you don't already have a creds database on your
[CouchDB](http://couchdb.apache.org/) configure the Key Store
by running the following in a new terminal window

~~~~~
cd; cd yar; source bin/cfg4dev; key_store_installer --log=info --create=true
~~~~~

* start the Key Server: in a new terminal window run the following to start the Key Server - by
default the Key Server will listen on 127.0.0.1:8070

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
  -d "{\"principal\":\"simonsdave@gmail.com\", \"auth_scheme\":\"hmac\"}" \
  http://127.0.0.1:8070/v1.0/creds
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

* start the Nonce Store: if [memcached](http://memcached.org/)
isn't already running, in a new terminal window start memcached using
the following command - by default [memcached](http://memcached.org/)
listens on port 11211

~~~~~
memcached -vv
~~~~~

* start the Authentication Server by running the following in a new terminal window - by
default, the Autentication Server listens on 127.0.0.1:8000

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
yarcurl GET http://127.0.0.1:8000/dave-was-here.html
~~~~~

