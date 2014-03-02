To start the authorization server:
~~~~~
auth_server
~~~~~

[auth_server](../../bin/auth_server) has a number of command
line options. Use the --help option to list them.

~~~~~
auth_server --help
Usage: auth_server [options]

Options:
  -h, --help            show this help message and exit
  --log=LOGGING_LEVEL   logging level
                        [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL] - default =
                        ERROR
  --lon=LISTEN_ON       address:port to listen on - default = [('127.0.0.1',
                        8000)]
  --authmethod=APP_SERVER_AUTH_METHOD
                        app server's authorization method - default = YAR
  --keyserver=KEY_SERVER
                        key server - default = 127.0.0.1:8070
  --appserver=APP_SERVER
                        app server - default = 127.0.0.1:8080
  --maxage=MAXAGE       max age (in seconds) of valid request - default = 30
  --noncestore=NONCE_STORE
                        memcached servers for nonce store - default =
                        ['127.0.0.1:11211']
  --syslog=SYSLOG       syslog unix domain socket - default = None
~~~~~

Instead of using cURL request to the app server thru the auth server it's
recommended that
[yarcurl.sh](https://github.com/simonsdave/yar/wiki/Utilities#yarcurlsh) be used.
yarcurl.sh is a very simple bash
script that computes the correct value for the HTTP Authorization header.
~~~~~

curl \
  -v \
  -X GET \
  -H "Authorization: MAC id=\"h480djs93hd8\", ts=\"00000\", nonce=\"264095:dj83hs9s\", ext=\"davsim\", mac=\"SLDJd4mg43cjQfElUs3Qub4L6xE=\"" \
  http://localhost:8000/dave.html
~~~~~
