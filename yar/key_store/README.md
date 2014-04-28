The Key Store is implemented as a [CouchDB](http://couchdb.apache.org/) database.
In the examples below, [CouchDB](http://couchdb.apache.org/) is assumed to be running
on localhost and listening on port 5984 and yar has been setup with the usual

To create a Key Store on a [CouchDB](http://couchdb.apache.org/) server
use [key_store_installer](../../bin/key_store_installer).

~~~~~
key_store_installer --log=INFO
~~~~~

[key_store_installer](../../bin/key_store_installer) has a number of command
line options. Use the --help option to list them.

~~~~~
key_store_installer --help
Usage: key_store_installer [options]

The Key Store Installer is a utility used to create and/or delete the CouchDB
database that implements yar's Key Store.

Options:
  -h, --help           show this help message and exit
  --log=LOGGING_LEVEL  logging level [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL]
                       - default = ERROR
  --host=HOST          where's CouchDB running - default = 127.0.0.1:5984
  --database=DATABASE  database - default = creds
  --delete=DELETE      delete before creating key store - default = False
  --create=CREATE      create key store - default = True
~~~~~

To create a new set of credentials for
[Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)
and save them to th Key Store

~~~~~
API_KEY=$(python -c "from yar.util.basic import APIKey; print APIKey.generate()")
CREDS="{\"principal\": \"dave@example.com\", \"type\": \"creds_v1.0\", \"is_deleted\": false, \"basic\": {\"api_key\": \"$API_KEY\"}}"
CONTENT_TYPE="Content-Type: application/json; charset=utf8"
curl -v -X PUT -H "$CONTENT_TYPE" -d "$CREDS" http://localhost:5984/creds/$API_KEY
~~~~~

To get an existing set of credentials used for
[Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)

~~~~~
curl -s http://localhost:5984/creds/<api key>
~~~~~

To create a new set of credentials for
[MAC Authentication](http://en.wikipedia.org/wiki/Message_authentication_code)
and save them to th Key Store

~~~~~
MAC_KEY_IDENTIFIER=$(python -c "from yar.util.mac import MACKeyIdentifier; print MACKeyIdentifier.generate()")
MAC_KEY=$(python -c "from yar.util.mac import MACKey; print MACKey.generate()")
MAC_ALGORITHM=$(python -c "from yar.util.mac import MAC; print MAC.algorithm")
CREDS="{\"principal\": \"dave@example.com\", \"type\": \"creds_v1.0\", \"is_deleted\": false, \"mac\": {\"mac_key\": \"$MAC_KEY\", \"mac_key_identifier\": \"$MAC_KEY_IDENTIFIER\", \"mac_algorithm\": \"$MAC_ALGORITHM\"}}"
CONTENT_TYPE="Content-Type: application/json; charset=utf8"
curl -v -X PUT -H "$CONTENT_TYPE" -d "$CREDS" http://localhost:5984/creds/$MAC_KEY_IDENTIFIER
~~~~~

To get an existing set of credentials used for
[MAC Authentication](http://en.wikipedia.org/wiki/Message_authentication_code)

~~~~~
curl -s http://localhost:5984/creds/<mac key identifier>
~~~~~

To get all credentials for a principal

~~~~~
curl -s 'http://localhost:5984/creds/_design/creds/_view/by_principal?key="dave@example.com"'
~~~~~

To delete an existing set of credentials used for
[Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)

~~~~~
API_KEY=<api key>
CREDS=$(curl -s http://localhost:5984/creds/$API_KEY | sed -e 's/"is_deleted":false/"is_deleted":true/g')
CONTENT_TYPE="Content-Type: application/json; charset=utf8"
curl -v -X PUT -H "$CONTENT_TYPE" -d "$CREDS" http://localhost:5984/creds/$API_KEY
~~~~~
