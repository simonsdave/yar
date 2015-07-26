#yar [![Build Status](https://travis-ci.org/simonsdave/yar.svg?branch=master)](https://travis-ci.org/simonsdave/yar) [![Requirements Status](https://requires.io/github/simonsdave/yar/requirements.svg?branch=master)](https://requires.io/github/simonsdave/yar/requirements/?branch=master) [![Coverage Status](http://coveralls.io/repos/simonsdave/yar/badge.svg?branch=master&service=github)](http://coveralls.io/github/simonsdave/yar?branch=master)
So you've spent time writing an awesome RESTful API and now you want to "secure it".
As you start Googling for a solution you'll quickly find there are
[a number of commerical API management solutions](docs/faq.md#what-other-api-management-solutions-exist)
available.
You'll also find there are lots of open source components that make it feel like
it should be pretty easy to stitch together your own API Management solution.
It's that last point that really motivated this project.
How hard could it really be?
Well, turned out to be more work than I originally thought (surprise)
but it wasn't crazy hard and it's been super interesting.
yar's about [1,200 logical lines of Python](bin/yarscm) and leverages a ton of amazing open source
components to provide a high quality, robust and feature rich
API Management solution.

When thinking about yar it's useful to have read [this story/vision](docs/story.md)
so you have some context.

So what is yar?
yar is a reverse proxy that sits in front of your RESTful API
to realize an API Management solution with the following
features/capabilities:

  * authentication of API requestors using
[MAC](http://en.wikipedia.org/wiki/Message_authentication_code)
and [Basic](http://en.wikipedia.org/wiki/Basic_authentication) authentication schemes - MACs
are calculated per the [OAuth 2.0 Message Authentication Code (MAC) Tokens](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02) specification
  * key generation for the above authentication schemes using [Keyczar](http://www.keyczar.org/)
  * [Auth Service](yar/auth_service) and [Key Service](yar/key_service) are built on [Tornado](http://www.tornadoweb.org/en/stable/) leveraging Tornado's [asynchronous/high concurrency capabilites](http://www.tornadoweb.org/en/stable/networking.html) - yar's high concurrency capability is verified with an [extensive and automated load testing framework](tests/load) that leverages [Vagrant](http://www.vagrantup.com/), [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Docker](https://www.docker.io/)
  * [horizontal scaability](http://en.wikipedia.org/wiki/Scalability#Horizontal_and_vertical_scaling)
of [Auth Services](yar/auth_service) and [Key Services](yar/key_service)
  * high quality code base - ~1,200 LLOC and 200+ unit tests with 99% code coverage
  * small footprint - the [Auth Service](yar/auth_service) and [Key Service](yar/key_service)
require < 25 MB of memory @ concurrency levels of 100
  * [Key Store](yar/key_store) is built on [CouchDB](http://couchdb.apache.org/) so the [Key Store](yar/key_store) inherits all the nice architectual/operational qualities of [CouchDB](http://couchdb.apache.org/)
  * intended deployment environment is [Ubuntu 12.04](http://releases.ubuntu.com/12.04.4/) and
development environment is [Mac OS X](http://www.apple.com/ca/osx/)

Is the project complete? Nope! yar is still a work in progress.
You can find the list of open issues [here](https://github.com/simonsdave/yar/issues?state=open).

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
> you'll find it hard to debug the error messages produced by **source cfg4dev**.

* get the source code by running the following in a new terminal window

~~~~~
cd; git clone https://github.com/simonsdave/yar.git
~~~~~

* start the App Service with the following in a new terminal window - by default the App
Service listens on 127:0.0.1:8080 - this App Service is only for
testing/development - you wouldn't use this in a production deployment:

~~~~~
cd; cd yar; source cfg4dev; app_service --log=info
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
cd; cd yar; source cfg4dev; key_store_installer --log=info --create=true
~~~~~

* start the Key Service: in a new terminal window run the following to start the Key Service - by
default the Key Service will listen on 127.0.0.1:8070

~~~~~
cd; cd yar; source cfg4dev; key_service --log=info
~~~~~

* generate an inital set of credentials by issuing the
follow [cURL](http://en.wikipedia.org/wiki/CURL) request:

~~~~~
curl \
  -v \
  -X POST \
  -H "Content-Type: application/json; charset=utf8" \
  -d "{\"principal\":\"simonsdave@gmail.com\", \"auth_scheme\":\"mac\"}" \
  http://127.0.0.1:8070/v1.0/creds
~~~~~

* using the credentials returned by the above [cURL](http://en.wikipedia.org/wiki/CURL)
request, create a new file called ~/.yar.creds
in the following format (this file will be used in a bit by
[yarcurl](bin/yarcurl)):

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

* start the Auth Service by running the following in a new terminal window - by
default, the Auth Service listens on 127.0.0.1:8000

~~~~~
cd; cd yar; source cfg4dev; auth_service --log=info
~~~~~

* Okay, all of your infrastructure should now be running!
Time to issue your first request to the App Service thru the Auth Service.
In a new terminal window issue the following commands to setup your PATH:

~~~~~
cd; cd yar; source cfg4dev
~~~~~

* In the same window that you executed the above commands, you'll now use
[yarcurl](bin/yarcurl)
to issue a request to the App Service via the Auth Service:

~~~~~
yarcurl GET http://127.0.0.1:8000/dave-was-here.html
~~~~~
