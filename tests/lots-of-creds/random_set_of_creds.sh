#!/usr/bin/env bash

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
source $SCRIPT_DIR_NAME/../util.sh

$SCRIPT_DIR_NAME/../rm_all_containers.sh

echo "Creating Key Store"
DATA_DIRECTORY=$(mktemp -d)
if ! KEY_STORE=$(create_key_store $DATA_DIRECTORY 50000); then
    echo "Failed to create key store"
    exit 1
fi
echo "Key Store available @ '$KEY_STORE'"
echo "Key Store data saved in '$DATA_DIRECTORY'"

curl \
    -s \
    -X PUT \
    -H "Content-Type: application/json; charset=utf8" \
    -d @$SCRIPT_DIR_NAME/random_set_of_creds.js \
    http://$KEY_STORE/_design/random_set_of_creds

curl -X GET http://$KEY_STORE/_design/random_set_of_creds/_view/all?key=42
