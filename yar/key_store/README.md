The Key Store is implemented as a [CouchDB](http://couchdb.apache.org/) database.
In the examples below, [CouchDB](http://couchdb.apache.org/) is assumed to be running
on localhost and listening on port 5984 and yar has been setup with the usual
~~~~~
cd; cd yar; source bin/cfg4dev; https://github.com/simonsdave/yar.git
~~~~~

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

To get all MAC credentials currently saved in the Key Store

~~~~~~
curl -s -X GET http://localhost:5984/creds/_design/creds/_view/all
~~~~~~

To get an existing set of credentials

~~~~~
curl -s -X GET http://localhost:5984/creds/<MAC key identifier>
~~~~~

To get all credentials for a principal

~~~~~
curl -s 'http://localhost:5984/creds/_design/creds/_view/by_principal?startkey="simonsdave@gmail.com"&endkey="simonsdave@gmail.com"'
~~~~~
