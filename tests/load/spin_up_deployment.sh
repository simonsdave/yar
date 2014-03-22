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

#
# parse command line arguments
#
SILENT=0
DOCKER_CONTAINER_DATA=""
DEPLOYMENT_PROFILE=""

while [[ 0 -ne $# ]]
do
    KEY="$1"
    shift
    case $KEY in
        -p|--profile)
            DEPLOYMENT_PROFILE=${1:-}
            shift
            ;;
        -d|--data)
            DOCKER_CONTAINER_DATA=${1:-}
            shift
            ;;
        -s|--silent)
            SILENT=1
            ;;
        *)
            echo "usage: `basename $0` [-s] [-d <docker container data dir>] [-p <profile>]"
            exit 1
            ;;
    esac
done

if [ "$DOCKER_CONTAINER_DATA" == "" ]; then
    DOCKER_CONTAINER_DATA=$(mktemp -d)
else
    if [ ! -d $DOCKER_CONTAINER_DATA ]; then
        echo "Can't find directory '$DOCKER_CONTAINER_DATA'"
        exit 2
    fi
fi

#
# spin up services
#

echo_if_not_silent "Starting Services ..."
echo_if_not_silent ""

echo_if_not_silent "Starting App Server(s)"
DATA_DIRECTORY=$DOCKER_CONTAINER_DATA/App-Server
if ! APP_SERVER=$(create_app_server $DATA_DIRECTORY); then
    echo_to_stderr_if_not_silent "App Server failed to start"
    exit 1
fi
echo_if_not_silent "$APP_SERVER in $DATA_DIRECTORY"

echo_if_not_silent "Starting App Server LB"
DATA_DIRECTORY=$DOCKER_CONTAINER_DATA/App-Server-LB
if ! APP_SERVER_LB=$(create_app_server_lb $DATA_DIRECTORY $APP_SERVER); then
    echo_to_stderr_if_not_silent "App Server failed to start"
    exit 1
fi
echo_if_not_silent "$APP_SERVER_LB in $DATA_DIRECTORY"

echo_if_not_silent "Starting Nonce Store"
DATA_DIRECTORY=$DOCKER_CONTAINER_DATA/Nonce-Store
if ! NONCE_STORE=$(create_nonce_store $DATA_DIRECTORY); then 
    echo_to_stderr_if_not_silent "Nonce Store failed to start"
    exit 1
fi
echo_if_not_silent "$NONCE_STORE in $DATA_DIRECTORY"

echo_if_not_silent "Starting Key Store"
EXISTING_CREDS=""
if [ "$DEPLOYMENT_PROFILE" != "" ]; then
    KEY_STORE_SIZE=`cat $DEPLOYMENT_PROFILE | get_from_json '\["key_store"\,"number_of_creds"\]'`
    if [ "$KEY_STORE_SIZE" != "" ]; then
        EXISTING_CREDS=$SCRIPT_DIR_NAME/lots-of-creds/$KEY_STORE_SIZE.creds.couch
    fi
fi
DATA_DIRECTORY=$DOCKER_CONTAINER_DATA/Key-Store
if ! KEY_STORE=$(create_key_store $DATA_DIRECTORY $EXISTING_CREDS); then 
    echo_to_stderr_if_not_silent "Key Store failed to start"
    exit 1
fi
echo_if_not_silent "$KEY_STORE in $DATA_DIRECTORY"

echo_if_not_silent "Starting Key Server"
DATA_DIRECTORY=$DOCKER_CONTAINER_DATA/Key-Server
if ! KEY_SERVER=$(create_key_server $DATA_DIRECTORY $KEY_STORE); then
    echo_to_stderr_if_not_silent "Key Server failed to start"
    exit 1
fi
echo_if_not_silent "$KEY_SERVER in $DATA_DIRECTORY"

echo_if_not_silent "Starting Auth Server"
DATA_DIRECTORY=$DOCKER_CONTAINER_DATA/Auth-Server
if ! AUTH_SERVER=$(create_auth_server $DATA_DIRECTORY $KEY_SERVER $APP_SERVER_LB $NONCE_STORE); then
    echo_to_stderr_if_not_silent "Auth Server failed to start"
    exit 1
fi
echo_if_not_silent "$AUTH_SERVER in $DATA_DIRECTORY"

echo_if_not_silent "Starting Auth Server LB"
DATA_DIRECTORY=$DOCKER_CONTAINER_DATA/Auth-Server-LB
AUTH_SERVER_LB=$(create_auth_server_lb $DATA_DIRECTORY $AUTH_SERVER)
if [ 1 -eq $SILENT ]; then
	echo $AUTH_SERVER_LB
else
	echo "$AUTH_SERVER_LB in $DATA_DIRECTORY"
fi

echo_if_not_silent ""
echo_if_not_silent "Deployment Description in ~/.yar.deployment"
cat_if_not_silent ~/.yar.deployment

# services now running, time to provision some keys

echo_if_not_silent ""
echo_if_not_silent "Creating Credentials ..."
PRINCIPAL="dave@example.com"
create_basic_creds $KEY_SERVER $PRINCIPAL
create_mac_creds $KEY_SERVER $PRINCIPAL
echo_if_not_silent ""
echo_if_not_silent "Credentials in ~/.yar.creds"
cat_if_not_silent ~/.yar.creds

exit 0
