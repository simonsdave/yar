The Key Store is implemented as a [CouchDB](http://couchdb.apache.org/) database.
In the examples below, [CouchDB](http://couchdb.apache.org/) is assumed to be running
on localhost and listening on port 5984.
It is also assumed that yar has been setup in the usual manner.

To create a Key Store on a [CouchDB](http://couchdb.apache.org/) server
use [key_store_installer](../../bin/key_store_installer).

[key_store_installer](../../bin/key_store_installer) has a number of command
line options. Use the --help option to list them.

~~~~~
(env)>key_store_installer --help
Usage: key_store_installer [options]

The Key Store Installer is a utility used to create and/or delete the CouchDB
database that implements yar's Key Store.

Options:
  -h, --help            show this help message and exit
  --log=LOGGING_LEVEL   logging level
                        [DEBUG,INFO,WARNING,ERROR,CRITICAL,FATAL] - default =
                        ERROR
  --host=HOST           where's CouchDB running - default = 127.0.0.1:5984
  --database=DATABASE   database - default = creds
  --delete=DELETE       delete before creating key store - default = False
  --create=CREATE       create key store - default = True
  --createdesign=CREATE_DESIGN_DOCS
                        create design docs - default = True
(env)>
~~~~~

To create a new set of credentials for
[Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)
and save them to the Key Store

~~~~~
API_KEY=$(python -c "from yar.util.basic import APIKey; print APIKey.generate()")
CREDS="{\"principal\": \"dave@example.com\", \"type\": \"creds_v1.0\", \"is_deleted\": false, \"basic\": {\"api_key\": \"$API_KEY\"}}"
CONTENT_TYPE="Content-Type: application/json; charset=utf8"
curl -v -X POST -H "$CONTENT_TYPE" -d "$CREDS" http://localhost:5984/creds
~~~~~

To get an existing set of credentials used for
[Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)

~~~~~
curl -s 'http://localhost:5984/creds/_design/by_identifier/_view/by_identifier?key="<API KEY>"'
~~~~~

To create a new set of credentials for
[MAC Authentication](http://en.wikipedia.org/wiki/Message_authentication_code)
and save them to the Key Store

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
curl -s 'http://localhost:5984/creds/_design/by_identifier/_view/by_identifier?key="<MAC KEY IDENTIFIER>"'
~~~~~

To get all credentials for a principal

~~~~~
curl -s 'http://localhost:5984/creds/_design/by_principal/_view/by_principal?key="dave@example.com"'
~~~~~

To delete an existing set of credentials used for
[Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)

~~~~~
API_KEY=<api key>
CREDS=$(curl -s http://localhost:5984/creds/$API_KEY | sed -e 's/"is_deleted":false/"is_deleted":true/g')
CONTENT_TYPE="Content-Type: application/json; charset=utf8"
curl -v -X PUT -H "$CONTENT_TYPE" -d "$CREDS" http://localhost:5984/creds/$API_KEY
~~~~~

# Design Notes

## Document Keys & UUIDs
In early versions of yar, the Key Store used the
[Basic Authentication](http://en.wikipedia.org/wiki/Basic_authentication)'s
API Key and MAC Key Identifier as the CouchDB document key.
It turns out that these kind of keys are not "CouchDB b-tree friendly".
What does this mean? The best
illustration of the problem came when exploring how the size of the
database grew as a function of the number of credentials
(see [this](../../tests/tests-key-store-size/) for test details).
After some Googling it became clear that the cause of the problem
was using Python's uuid.uuid4() for document keys and
PUTing new documents into CouchDB rather than using CouchDB's own
UUIDs and POSTing new documents.

> So, the CouchDB design pattern that's used for document keys is:
* POST to create documents and let CouchDB generate its own UUID for the
new document
* documents probably have a natural key that you would have liked to use
as the document key; include this key as a document attribute and create
a few to permit retrieval of documents by the natural key

## Design Docs & Views
In the above you may noticed that all of yar's CouchDB views are maintained
within there own design document. Early versions of yar had a single design
document containing many views but this was changed as operational experience
was gained with CouchDB (mostly through load testing) when the following kinds
of things where learned
* you only compact design document not views
(see [this](http://couchdb.readthedocs.org/en/latest/maintenance/compaction.html#views-compaction))
* you can only get metrics about design documents not views
(see [this](http://couchdb.readthedocs.org/en/latest/api/ddoc/common.html?highlight=_info#get--db-_design-ddoc-_info]))

> So, the CouchDB design pattern that used for view storage is:
* every view is stored in its own design document

# Operational Notes

To get metrics on the creds database

~~~~~
curl -s http://localhost:5984/creds | python -mjson.tool
{
    "committed_update_seq": 100001,
    "compact_running": false,
    "data_size": 38050910,
    "db_name": "creds",
    "disk_format_version": 6,
    "disk_size": 49496177,
    "doc_count": 100001,
    "doc_del_count": 0,
    "instance_start_time": "1401746975591983",
    "purge_seq": 0,
    "update_seq": 100001
}
~~~~~

To get the list of all views in the creds database
(request below based on [this](http://stackoverflow.com/questions/2814352/get-all-design-documents-in-couchdb))

~~~~~
curl -s 'http://localhost:5984/creds/_all_docs?startkey="_design"&endkey="_design0"' | python -mjson.tool
{
    "offset": 62651,
    "rows": [
        {
            "id": "_design/creds",
            "key": "_design/creds",
            "value": {
                "rev": "1-893becf62a1444aedb82aeacda0f2100"
            }
        }
    ],
    "total_rows": 100001
}
~~~~~

To get metrics on the by_identifier design document

~~~~~
curl -s http://localhost:5984/creds/_design/by_identifier/_info | python -mjson.tool
{
    "name": "creds",
    "view_index": {
        "compact_running": false,
        "data_size": 0,
        "disk_size": 51,
        "language": "javascript",
        "purge_seq": 0,
        "signature": "d892d333ca8f8ec8a7850c3e6d5e5285",
        "update_seq": 0,
        "updater_running": false,
        "waiting_clients": 0,
        "waiting_commit": false
    }
}
~~~~~

See [CouchDB reference manual](http://couchdb.readthedocs.org/en/latest/maintenance/compaction.html)
for lots of details. The manual does a good outlining
[database compaction](http://couchdb.readthedocs.org/en/latest/maintenance/compaction.html#database-compaction)
and
[view compaction](http://couchdb.readthedocs.org/en/latest/maintenance/compaction.html#views-compaction).
