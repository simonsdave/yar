The app server is a very simple HTTP server for use
during testing and development of yar.

To start the app server:

~~~~~
app_server --log=info
~~~~~

[app_server](../../bin/app_server) has a number of command
line options. Use the --help option to list them.

~~~~~
app_server --help
Usage: app_server [options]

Options:
  -h, --help           show this help message and exit
  --log=LOGGING_LEVEL  logging level [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL]
                       - default = ERROR
  --lon=LISTEN_ON      port - default = [('127.0.0.1', 8080)]
  --syslog=SYSLOG      syslog unix domain socket - default = None
~~~~~

The app server responds to all standard HTTP requests.
To confirm the app server is working correctly try a simple curl request.

~~~~~
curl http://127.0.0.1:8080/dave.html
{
    "auth": "<no auth header>",
    "status": "ok",
    "when": "2014-03-03 05:35:58.560929"
}
~~~~~

