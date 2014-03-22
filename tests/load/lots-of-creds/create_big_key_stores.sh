#!/usr/bin/env bash

# this script creates ...

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
DATA_DIRECTORY=$(mktemp -d)
if ! KEY_STORE=$(create_key_store $DATA_DIRECTORY); then
    echo "Failed to create key store"
    exit 1
fi
echo "Key Store available @ '$KEY_STORE'"
echo "Key Store data saved in '$DATA_DIRECTORY'"

#
# iterate over each of the json files containing previously
# generated credentials taking a copy of the key store after
# each millionth upload and save the copy to the same
# directory as this script
#
TOTAL_NUMBER_OF_CREDS=0
# for CREDS in $SCRIPT_DIR_NAME/*.json
for CREDS in $SCRIPT_DIR_NAME/000[0-5]-*.json
do
    echo "Uploading $CREDS"

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
    if [ $(($TOTAL_NUMBER_OF_CREDS % 10000)) == 0 ];then
        cp $DATA_DIRECTORY/data/creds.couch $SCRIPT_DIR_NAME/$TOTAL_NUMBER_OF_CREDS.creds.couch
    fi

done

exit 0
