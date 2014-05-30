To start the Auth Service:

~~~~~
auth_service
~~~~~

[auth_service](../../bin/auth_service) has a number of command
line options. Use the --help option to list them.

~~~~~
(env)>auth_service --help
Usage: auth_service [options]

Options:
  -h, --help            show this help message and exit
  --log=LOGGING_LEVEL   logging level
                        [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL] - default =
                        ERROR
  --lon=LISTEN_ON       address:port to listen on - default = 127.0.0.1:8000
  --appserviceauthmethod=APP_SERVICE_AUTH_METHOD
                        app service's authorization method - default = YAR
  --keyservice=KEY_SERVICE
                        key service - default = 127.0.0.1:8070
  --appserver=APP_SERVICE
                        app service - default = 127.0.0.1:8080
  --maxage=MAXAGE       max age (in seconds) of valid request - default = 30
  --noncestore=NONCE_STORE
                        memcached servers for nonce store - default =
                        ['127.0.0.1:11211']
  --syslog=SYSLOG       syslog unix domain socket - default = None
  --logfile=LOGGING_FILE
                        log to this file - default = None
~~~~~

When starting to use infrastructure like the Auth Service the natural instinct
would be to send the Auth Service a request using [cURL](http://en.wikipedia.org/wiki/CURL).
[cURL](http://en.wikipedia.org/wiki/CURL) is very effective when
using [Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)

~~~~~
curl -s -u c4a8dfc4cb4b40a2a6bf1102720d9a06: http://127.0.0.1:5984/dave-was-here.html
~~~~~

To issue requests to the Auth Service using
[OAuth 2.0 Message Authentication Code (MAC) Tokens](http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02)
authentication [yarcurl](../../bin/yarcurl) is the recommended command line tool
rather than [cURL](http://en.wikipedia.org/wiki/CURL).

~~~~~
yarcurl GET http://127.0.0.1:5984/dave-was-here.html
~~~~~
