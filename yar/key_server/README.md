To start the Key Server:
~~~~~
key_server
~~~~~
By default the Key Server will attempt to listen on 127.0.0.1:8070 and connect to
a [Key Store](https://github.com/simonsdave/yar/wiki/Key-Store)
at localhost:5984/creds.
For a complete list of the Key Server's command line options try:
~~~~~
key_server --help
~~~~~
The Key Server is configured using command line options.
No configuration file is used.

All credentials are "owned" by someone.
An owner's identity is represented below as an opaque string at least one character long.
To create a set of credentials:
~~~~~~
curl \
  -v \
  -X POST \
  -H "Content-Type: application/json; charset=utf8" \
  -d "{\"owner\":\"simonsdave@gmail.com\"}" \
  http://localhost:8070/v1.0/creds
~~~~~~
To get an existing set of credentials:
~~~~~
curl \
  -v \
  -X GET \
  http://localhost:6969/v1.0/creds/<MAC key identifier>
~~~~~
To get all credentials currently saved in the
[Key Store](https://github.com/simonsdave/yar/wiki/Key-Store):
~~~~~~
curl \
  -s \
  -X GET \
  http://localhost:8070/v1.0/creds
~~~~~~
To get all credentials with a specific owner:
~~~~~
curl -X GET http://localhost:8070/v1.0/creds?owner=<owner>
~~~~~
To get all credentials including those that have been deleted:
~~~~~
curl -X GET http://localhost:8070/v1.0/creds?deleted=true
~~~~~
To delete a set of existing credentials:
~~~~~
curl \
  -v \
  -X DELETE \
  http://localhost:6969/v1.0/creds/<MAC key identifier>
~~~~~
