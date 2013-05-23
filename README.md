This repo is the result of Dave being convinced that it wouldn't be that
hard to write an API Management service.
See the [Wiki](https://github.com/simonsdave/yar/wiki) for a more complete description and discussion of yar.

Prerequisites 
-------------
* code written and tested on Mac OS X 10.8.2 using
Python 2.7.2,
[nose 1.3.0](https://github.com/nose-devs/nose)
and [virtualenv 1.9.1](https://pypi.python.org/pypi/virtualenv)
* see [requirements.txt](https://github.com/simonsdave/yar/blob/master/requirements.txt "requirements.txt") for the complete list of prerequisites

Development
-----------
The following (brief) instructions describe how to setup a yar development environment and
issue your first request through the infrastructure.
The commands below are expected to be executed in your
favorite terminal emulator ([iTerm2](http://www.iterm2.com/) happens to be Dave's favorite).
In the instructions below it's assumed yar is installed to your home directory.
* get the source code by running the following in a new terminal window

~~~~~
cd; git clone https://github.com/simonsdave/yar.git
~~~~~

* start the App Server with the following in a new terminal window
(this app server is only for testing/development - you wouldn't use this in a production deployment):

~~~~~
cd; cd yar; source bin/cfg4dev; cd app_server; ./app_server.py --log=info
~~~~~

* start the Key Store - if CouchDB isn't already running, in a new terminal window start CouchDB using

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

* generating an inital set of credentials: in any available terminal window (feel free to use your own e-mail address):

~~~~~
curl \
  -v \
  -X POST \
  -H "Content-Type: application/json; charset=utf8" \
  -d "{\"owner\":\"simonsdave@gmail.com\"}" \
  http://localhost:8070/v1.0/creds
~~~~~

* using the credentials returned by the above cURL request, create a new file called ~/.yar.creds
in the following format (this file will be used in a bit by
[yarcurl.sh](https://github.com/simonsdave/yar/wiki/Utilities#yarcurlsh)):

~~~~~
MAC_KEY_IDENTIFIER=484e15185fd50b7292f4b3ae08d45576
MAC_KEY=6b656577695f4361474578704436552d50706541444172476c776d6b64754f704545786e65613976595734
MAC_ALGORITHM=hmac-sha-1
~~~~~

* start Nonce Store: if memcached isn't already running, in a new terminal window start memcached using

~~~~~
memcached -vv
~~~~~

* start the Authentication Server by running the following in a new terminal window

~~~~~
cd; cd yar; source bin/cfg4dev; cd auth_server; ./auth_server.py --log=info
~~~~~

* Okay, all of your infrastructure should not be running!
Time to issue your first request to the app server thru the authentication server.
In a new terminal window issue the following commands to setup your PATH:

~~~~~
cd; cd yar; source bin/cfg4dev
~~~~~

* In the same window that you executed the above commands, you'll now use
[yarcurl.sh](https://github.com/simonsdave/yar/wiki/Utilities#yarcurlsh) 
to issue a request to the app server via the auth server:

~~~~~
yarcurl.sh GET /das.html
~~~~~

