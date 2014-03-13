#!/usr/bin/env bash

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

source $SCRIPT_DIR_NAME/util.sh

create_basic_creds() {

    KEY_SERVER=${1:-}
    PRINCIPAL=${2:-}

    CREDS_FILE_NAME=$(mktemp)

    curl \
        -s \
        -X POST \
        -H "Content-Type: application/json; charset=utf8" \
        -d "{\"principal\":\"$PRINCIPAL\", \"auth_scheme\":\"basic\"}" \
        http://$KEY_SERVER/v1.0/creds > $CREDS_FILE_NAME

    local API_KEY=`cat $CREDS_FILE_NAME | get_from_json '\["basic"\,"api_key"\]'`

    echo "API_KEY=$API_KEY" >> ~/.yar.creds

    rm -rf $CREDS_FILE_NAME >& /dev/null
}

create_mac_creds() {

    KEY_SERVER=${1:-}
    PRINCIPAL=${2:-}

    CREDS_FILE_NAME=$(mktemp)

    curl \
        -s \
        -X POST \
        -H "Content-Type: application/json; charset=utf8" \
        -d "{\"principal\":\"$PRINCIPAL\", \"auth_scheme\":\"hmac\"}" \
        http://$KEY_SERVER/v1.0/creds > $CREDS_FILE_NAME

    local MAC_ALGORITHM=`cat $CREDS_FILE_NAME | get_from_json \
        '\["hmac"\,"mac_algorithm"\]'`

    local MAC_KEY_IDENTIFIER=`cat $CREDS_FILE_NAME | get_from_json \
        '\["hmac"\,"mac_key_identifier"\]'`

    local MAC_KEY=`cat $CREDS_FILE_NAME | get_from_json \
        '\["hmac"\,"mac_key"\]'`

    echo "MAC_KEY_IDENTIFIER=$MAC_KEY_IDENTIFIER" >> ~/.yar.creds
    echo "MAC_KEY=$MAC_KEY" >> ~/.yar.creds
    echo "MAC_ALGORITHM=$MAC_ALGORITHM" >> ~/.yar.creds

    rm -rf $CREDS_FILE_NAME >& /dev/null
}

echo_if_not_silent() {
    if [ 0 -eq $SILENT ]; then
        echo $1
    fi
}

cat_if_not_silent() {
    if [ 0 -eq $SILENT ]; then
        cat $1
    fi
}

# the script accepts an optional -s command line argument.
# if -s exists set SILENT to 1 otherwise SILENT is set to 0.
SILENT=0
if [ 2 -le $# ]; then
    if [ "-s" == $1 ]; then
        SILENT=1
        shift
    fi
fi

# the script accepts an optional single command line argument
# which is the name of the directory in which all docker
# container files should be placed. if no such argument exists
# create a temp directory
if [ $# == 0 ]; then
    DOCKER_CONTAINER_DATA=$(mktemp -d)
else
    if [ $# == 1 ]; then
        DOCKER_CONTAINER_DATA=$1
        if [ ! -d $DOCKER_CONTAINER_DATA ]; then
            echo "Can't find directory '$DOCKER_CONTAINER_DATA'"
            exit 1
        fi
    else
        echo "usage: `basename $0` [-s] [<docker container data dir>]"
        exit 1
    fi
fi

# spin up services

echo_if_not_silent "Starting Services ..."
echo_if_not_silent ""

echo_if_not_silent "Starting App Server(s)"
DATA_DIRECTORY=$DOCKER_CONTAINER_DATA/App-Server
APP_SERVER=$(create_app_server $DATA_DIRECTORY)
echo_if_not_silent "$APP_SERVER in $DATA_DIRECTORY"

echo_if_not_silent "Starting App Server LB"
APP_SERVER_LB=$(create_app_server_lb $APP_SERVER)
echo_if_not_silent $APP_SERVER_LB

echo_if_not_silent "Starting Nonce Store"
NONCE_STORE=$(create_nonce_store) 
echo_if_not_silent $NONCE_STORE

echo_if_not_silent "Starting Key Store"
DATA_DIRECTORY=$DOCKER_CONTAINER_DATA/Key-Store
KEY_STORE=$(create_key_store $DATA_DIRECTORY) 
echo_if_not_silent "$KEY_STORE in $DATA_DIRECTORY"

echo_if_not_silent "Starting Key Server"
DATA_DIRECTORY=$DOCKER_CONTAINER_DATA/Key-Server
KEY_SERVER=$(create_key_server $DATA_DIRECTORY $KEY_STORE)
echo_if_not_silent "$KEY_SERVER in $DATA_DIRECTORY"

echo_if_not_silent "Starting Auth Server"
DATA_DIRECTORY=$DOCKER_CONTAINER_DATA/Auth-Server
AUTH_SERVER=$(create_auth_server $DATA_DIRECTORY $KEY_SERVER $APP_SERVER_LB $NONCE_STORE)
echo_if_not_silent "$AUTH_SERVER in $DATA_DIRECTORY"

echo_if_not_silent "Starting Auth Server LB"
AUTH_SERVER_LB=$(create_auth_server_lb $AUTH_SERVER)
echo $AUTH_SERVER_LB

# services now running, time to provision some keys

echo_if_not_silent ""
echo_if_not_silent "Creating Credentials ..."
PRINCIPAL="dave@example.com"
rm -f ~/.yar.creds >& /dev/null
create_basic_creds $KEY_SERVER $PRINCIPAL
create_mac_creds $KEY_SERVER $PRINCIPAL
echo_if_not_silent ""
echo_if_not_silent "Credentials in ~/.yar.creds"
cat_if_not_silent ~/.yar.creds

exit 0
