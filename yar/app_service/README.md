The app service responds to HTTP requests with JSON
documents and is intended for use during testing and
development of yar.

To start the app service:

~~~~~
app_service
~~~~~

[app_service](../../bin/app_service) has a number of command
line options. Use the --help option to list them.

~~~~~
(env)>app_service --help
Usage: app_service [options]

Options:
  -h, --help            show this help message and exit
  --log=LOGGING_LEVEL   logging level
                        [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL] - default =
                        ERROR
  --lon=LISTEN_ON       port - default = [('127.0.0.1', 8080)]
  --syslog=SYSLOG       syslog unix domain socket - default = None
  --logfile=LOGGING_FILE
                        log to this file - default = None
(env)>
~~~~~

The app service responds to all the standard HTTP requests.
To confirm the app service is working correctly try a simple curl request.

~~~~~
curl http://127.0.0.1:8080/dave.html
{
    "auth": "<no auth header>",
    "status": "ok",
    "when": "2014-03-03 05:35:58.560929"
}
~~~~~
