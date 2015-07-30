#!/usr/bin/env python

import datetime
import httplib
import json
import time
import uuid

import requests

base_url = "https://127.0.0.1:8445"


def create_database(host, db):
    url = "%s/%s" % (host, db)

    response = requests.get(url)
    if response.status_code == httplib.OK:
        response = requests.delete(url)
        if response.status_code != httplib.OK:
            print "Error deleting database '%s'" % url
            return False
        else:
            print "Successfully deleted database '%s'" % url

    response = requests.put(url)
    if response.status_code != httplib.CREATED:
        print "Error creating database '%s'" % url
        return False

    url = "%s/%s/_design/conflicts" % (host, db)
    headers = {
        "Content-Type": "application/json",
    }
    view = (
        '{'
        '    "language": "javascript",'
        '    "views": {'
        '        "conflicts": {'
        '            "map": "function(doc) { if(doc._conflicts) { emit(doc._conflicts, null); } }"'
        '        }'
        '    }'
        '}'
    )
    response = requests.put(
        url,
        headers=headers,
        data=view)
    if response.status_code != httplib.CREATED:
        print "Error creating conflicts view"
        return False

    print "Successfully created database '%s'" % url
    return True


def fire_replication(host, source_db, target_db):
    payload = {
        "source": source_db,
        "target": target_db,
    }
    headers = {
        "Content-Type": "application/json",
    }
    url = "%s/_replicate" % host
    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(payload))
    if response.status_code != httplib.OK:
        print "Error firing replication from '%s' to '%s'" % (source_db, target_db)
        return False

    print "Successfully fired replication from '%s' to '%s'" % (source_db, target_db)
    return True


def create_document(host, db):
    doc_id = uuid.uuid4().hex
    payload = {
        "ts": datetime.datetime.now().isoformat(),
    }
    headers = {
        "Content-Type": "application/json",
    }
    url = "%s/%s/%s" % (host, db, doc_id)
    response = requests.put(
        url,
        headers=headers,
        data=json.dumps(payload))
    if response.status_code != httplib.CREATED:
        print "Error creating document '%s':-(" % url
        return None

    fmt = "Successfully created doc (id = '%s') document on '%s/%s' :-("
    print fmt % (doc_id, host, db)
    return doc_id


def get_document(host, db, doc_id):
    url = "%s/%s/%s" % (host, db, doc_id)
    response = requests.get(url)
    if response.status_code != httplib.OK:
        print "Error getting document '%s':-(" % url
        return None

    return response.json()


def update_document(host, db, doc):
    doc_id = doc["_id"]
    doc["ts"] = datetime.datetime.now().isoformat()
    headers = {
        "Content-Type": "application/json",
    }
    url = "%s/%s/%s" % (host, db, doc_id)
    response = requests.put(
        url,
        headers=headers,
        data=json.dumps(doc))
    if response.status_code != httplib.CREATED:
        print "Error creating updating '%s':-(" % url
        return None

    fmt = "Successfully updated doc (id = '%s') document on '%s/%s' :-("
    print fmt % (doc_id, host, db)
    return doc_id


def main():
    host = "http://localhost:5984"
    db1 = "dave001"
    db2 = "dave002"

    create_database(host, db1)
    create_database(host, db2)

    doc_id = create_document(host, db1)
    if not doc_id:
        return False
    doc = get_document(host, db1, doc_id)
    print "DB1 >>>%s<<<" % doc

    if not fire_replication(host, db1, db2):
        return False

    doc = get_document(host, db2, doc_id)
    print "DB2 >>>%s<<<" % doc

    print "%s/%s/%s" % (host, db1, doc_id)

    doc = get_document(host, db1, doc_id)
    update_document(host, db1, doc)
    doc = get_document(host, db1, doc_id)
    print "DB1 >>>%s<<<" % doc

    doc = get_document(host, db2, doc_id)
    update_document(host, db2, doc)
    doc = get_document(host, db2, doc_id)
    print "DB2 >>>%s<<<" % doc

    if not fire_replication(host, db1, db2):
        return False

    if not fire_replication(host, db2, db1):
        return False

    doc = get_document(host, db1, doc_id)
    print "DB1 >>>%s<<<" % doc
    doc = get_document(host, db2, doc_id)
    print "DB2 >>>%s<<<" % doc

    # curl http://localhost:5984/dave002/_design/conflicts/_view/conflicts

main()
