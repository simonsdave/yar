This repo is the result of Dave being convinced that it wouldn't be that
hard to write an API Management service.
See the [wiki](https://github.com/simonsdave/yar/wiki) for a more complete description and discussion of yar.

Prerequisites 
-------------
* code written and tested on Mac OS X 10.8.2 using
Python 2.7.2,
[nose 1.3.0](https://github.com/nose-devs/nose)
and [virtualenv 1.9.1](https://pypi.python.org/pypi/virtualenv)
* see [requirements.txt](https://github.com/simonsdave/yar/blob/master/requirements.txt "requirements.txt") for the complete list of prerequisites

Development
-----------
The following brief set of instructions describe how to setup a yar development environment.
The sets below are expected to be executed in your
favorite terminal emulator ([iTerm2](http://www.iterm2.com/) happens to be Dave's favorite).
In the instructions below it's assumed yar is installed to your home directory.
* get the source code by running the following in a new terminal window

~~~~~
* cd; git clone https://github.com/simonsdave/yar.git
~~~~~

* start Key Store - if CouchDB isn't already running, in a new terminal window start CouchDB using

~~~~~
couchdb
~~~~~

* configure the Key Store: assuming you don't already have a creds database on your CouchDB configure Key Store
by running the following in a new terminal window

~~~~~
cd; cd yar; source bin/cfg4dev; cd key_server/key_store/; ./key_store_installer.py --log=info --create=true
~~~~~

* start the Key Server: in a new terminal window run the following to start the Key Server

~~~~~
cd; cd yar; source bin/cfg4dev; cd key_server; ./key_server.py --log=info
~~~~~

* start Nonce Store: if memcached isn't already running, in a new terminal window start memcached using

~~~~~
memcached -vv
~~~~~

* start the Authentication Server by running the following in a new terminal window

~~~~~
cd; cd yar; source bin/cfg4dev; cd auth_server; ./auth_server.py --log=info
~~~~~

