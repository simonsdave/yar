To start the app server:

~~~~~
app_server --log=info
~~~~~

By default the app server will attempt to use port 127.0.0.1:8080.

The app server will respond to HTTP GET, POST, DELETE and PUT requests.
To confirm the app server is working correctly try

~~~~~
curl http://localhost:8080/dave.html
~~~~~

