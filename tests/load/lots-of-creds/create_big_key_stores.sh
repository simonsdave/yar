#!/usr/bin/env bash

# when running load tests the key store should be loaded with
# a bunch of credentials so its data shape is representive of
# a real production scenario
#
# it takes a long time to load lots of creds into a CouchDB database
# so generating creds and loading them into CouchDB while running
# a load tests isn't desirable. instead, this script can be run
# outside of the load test to generate .couch files for CouchDB
# databases containing various numbers of credentails. armed
# with the .couch files it's quick to start a key store aginst
# the .couch file in effect almost instantly creating a key
# store with lots of credentials.

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
source $SCRIPT_DIR_NAME/../util.sh

#
# this script accepts no command line arguments
#
if [ $# != 0 ]; then
    echo "usage: `basename $0`"
    exit 1
fi

#
# create a key store in an isolated container
#
echo "Creating Key Store"
DATA_DIRECTORY=$(mktemp -d)
if ! KEY_STORE=$(create_key_store $DATA_DIRECTORY "" false); then
    echo "Failed to create key store"
    exit 1
fi
echo "Key Store available @ '$KEY_STORE'"
echo "Key Store data saved in '$DATA_DIRECTORY'"

#
# remove all old databases
#
echo "Removing all old databases from '$SCRIPT_DIR_NAME'"
rm -f $SCRIPT_DIR_NAME/*.creds.couch >& /dev/null

#
# iterate over each of the json files containing previously
# generated credentials taking a copy of the key store after
# each millionth upload and save the copy to the same
# directory as this script
#
TOTAL_NUMBER_OF_CREDS=0
# for CREDS in $SCRIPT_DIR_NAME/*.json
# for CREDS in $SCRIPT_DIR_NAME/00[0-5][0-9]-*.json
for CREDS in $SCRIPT_DIR_NAME/000[0-9]-*.json
do
    echo "Uploading '$CREDS'"

    curl \
        -s \
        -X POST \
        -H "Content-Type: application/json; charset=utf8" \
        -d @$CREDS \
        http://$KEY_STORE/_bulk_docs \
        >& /dev/null
    if [ $? != 0 ];then
        echo "Failed to upload '$CREDS' to key store @ '$$KEY_STORE'"
        exit 2
    fi

    NUMBER_OF_CREDS=$(echo $CREDS | sed s/\\/.*\\/[[:digit:]]*-0*// | sed s/.json$//)
    TOTAL_NUMBER_OF_CREDS=$(python -c "print $TOTAL_NUMBER_OF_CREDS + int($NUMBER_OF_CREDS)")
    if [ $(($TOTAL_NUMBER_OF_CREDS % 100000)) == 0 ];then
        SECONDS_TO_SLEEP=10
        echo "Sleeping $SECONDS_TO_SLEEP seconds to give CouchDB time to flush to disk"
        sleep $SECONDS_TO_SLEEP
        DEST=$SCRIPT_DIR_NAME/$TOTAL_NUMBER_OF_CREDS.creds.couch
        echo "Creating '$DEST'"
        cp $DATA_DIRECTORY/data/creds.couch $DEST
    fi

done

exit 0
