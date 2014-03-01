The key store is implemented as a CouchDB database.
In the examples below, CouchDB is assumed to be running on localhost and listening on port 5984.
To create the key store:
~~~~~
./key_store_installer.py --log=INFO --delete=true
~~~~~
To get all MAC credentials currently saved in the key store:
~~~~~~
curl -s -X GET http://localhost:5984/creds/_design/creds/_view/all
~~~~~~
To get an existing set of creditials:
~~~~~
curl -s -X GET http://localhost:5984/creds/<MAC key identifier>
~~~~~
To get all credentials for a particular owner:
~~~~~
curl -s -X GET 'http://localhost:5984/creds/_design/creds/_view/by_owner?startkey="simonsdave@gmail.com"&endkey="simonsdave@gmail.com"'
~~~~~
