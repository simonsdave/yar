#!/usr/bin/env bash

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"
source $SCRIPT_DIR_NAME/util.sh

create_basic_creds() {

    KEY_SERVICE=${1:-}
    PRINCIPAL=${2:-}

    CREDS_FILE_NAME=$(mktemp)

    curl \
        -s \
        -X POST \
        -H "Content-Type: application/json; charset=utf8" \
        -d "{\"principal\":\"$PRINCIPAL\", \"auth_scheme\":\"basic\"}" \
        http://$KEY_SERVICE/v1.0/creds > $CREDS_FILE_NAME

    local API_KEY=`cat $CREDS_FILE_NAME | get_from_json '\["basic"\,"api_key"\]'`

    echo "API_KEY=$API_KEY" >> ~/.yar.creds

    rm -rf $CREDS_FILE_NAME >& /dev/null
}

create_mac_creds() {

    KEY_SERVICE=${1:-}
    PRINCIPAL=${2:-}

    CREDS_FILE_NAME=$(mktemp)

    curl \
        -s \
        -X POST \
        -H "Content-Type: application/json; charset=utf8" \
        -d "{\"principal\":\"$PRINCIPAL\", \"auth_scheme\":\"mac\"}" \
        http://$KEY_SERVICE/v1.0/creds > $CREDS_FILE_NAME

    local MAC_ALGORITHM=`cat $CREDS_FILE_NAME | get_from_json \
        '\["mac"\,"mac_algorithm"\]'`

    local MAC_KEY_IDENTIFIER=`cat $CREDS_FILE_NAME | get_from_json \
        '\["mac"\,"mac_key_identifier"\]'`

    local MAC_KEY=`cat $CREDS_FILE_NAME | get_from_json \
        '\["mac"\,"mac_key"\]'`

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
# creating a temporary empty deployment profile just means we don't
# have to constantly code for "is there a profile do X else do Y"
#
if [ "$DEPLOYMENT_PROFILE" == "" ]; then
    DEPLOYMENT_PROFILE=$(platform_safe_mktemp)
    echo "{}" >> $DEPLOYMENT_PROFILE
fi

#
# some cleanup before we start the meat of this script
#
yar_init_deployment "$DOCKER_CONTAINER_DATA"

#
# App Service
#
echo_if_not_silent "Starting App Service(s)"

NUMBER_APP_SERVICES_PATTERN='\["app_service"\,"number_of_services"\]'
NUMBER_APP_SERVICES=$(get_from_json "$NUMBER_APP_SERVICES_PATTERN" "1" < $DEPLOYMENT_PROFILE)

for APP_SERVICE_NUMBER in $(seq 1 $NUMBER_APP_SERVICES)
do
    echo_if_not_silent "-- $APP_SERVICE_NUMBER: Starting App Service"
	if ! APP_SERVICE=$(create_app_service); then
		echo_to_stderr_if_not_silent "-- $APP_SERVICE_NUMBER: App Service failed to start"
		exit 1
	fi
	echo_if_not_silent "-- $APP_SERVICE_NUMBER: App Service listening on $APP_SERVICE"
done

#
# App Service LB
#
echo_if_not_silent "Starting App Service LB"
if ! APP_SERVICE_LB=$(create_app_service_lb); then
    echo_to_stderr_if_not_silent "-- App Service LB failed to start"
    exit 1
fi
echo_if_not_silent "-- App Service LB listening on $APP_SERVICE_LB"

#
# Nonce Store(s)
#
echo_if_not_silent "Starting Nonce Store(s)"

NUMBER_NONCE_STORES_PATTERN='\["nonce_store"\,"number_of_servers"\]'
NUMBER_NONCE_STORES=$(get_from_json "$NUMBER_NONCE_STORES_PATTERN" "1" < $DEPLOYMENT_PROFILE)

NONCE_STORES=""
for NONCE_STORE_NUMBER in $(seq 1 $NUMBER_NONCE_STORES)
do
    echo_if_not_silent "-- $NONCE_STORE_NUMBER: Starting Nonce Store"
    if ! NONCE_STORE=$(create_nonce_store); then 
        echo_to_stderr_if_not_silent "-- $NONCE_STORE_NUMBER: Nonce Store failed to start"
        exit 1
    fi
    NONCE_STORES="$NONCE_STORES,$NONCE_STORE"
    echo_if_not_silent "-- $NONCE_STORE_NUMBER: Nonce Store listening on $NONCE_STORE"
done
NONCE_STORES=$(echo $NONCE_STORES | sed -e "s/^\,//g")

#
# Key Store
#
echo_if_not_silent "Starting Key Store"

KEY_STORE_SIZE=""
if [ "$DEPLOYMENT_PROFILE" != "" ]; then
    KEY_STORE_SIZE=$(cat $DEPLOYMENT_PROFILE | \
        get_from_json '\["key_store"\,"number_of_creds"\]' "")
fi

PERCENT_BASIC_CREDS=90
if [ "$DEPLOYMENT_PROFILE" != "" ]; then
    PERCENT_BASIC_CREDS=$(cat $DEPLOYMENT_PROFILE | \
        get_from_json '\["key_store"\,"percent_basic_creds"\]' "")
fi

if ! KEY_STORE=$(create_key_store $KEY_STORE_SIZE $PERCENT_BASIC_CREDS); then 
    echo_to_stderr_if_not_silent "-- Key Store failed to start"
    exit 1
fi

echo_if_not_silent "-- Key Store listening on $KEY_STORE"

if [ "$DEPLOYMENT_PROFILE" != "" ]; then
    PERCENT_ACTIVE_CREDS=$(cat $DEPLOYMENT_PROFILE | \
        get_from_json '\["key_store"\,"percent_active_creds"\]' "")
    if [ "$PERCENT_ACTIVE_CREDS" != "" ]; then 
        echo_if_not_silent "-- Extracting random $PERCENT_ACTIVE_CREDS% of Key Store's creds"
        extract_random_set_of_creds_from_key_store $KEY_STORE $PERCENT_ACTIVE_CREDS
    fi
fi

#
# Key Service
#
echo_if_not_silent "Starting Key Service(s)"

NUMBER_KEY_SERVICES_PATTERN='\["key_service"\,"number_of_services"\]'
NUMBER_KEY_SERVICES=$(get_from_json "$NUMBER_KEY_SERVICES_PATTERN" "1" < $DEPLOYMENT_PROFILE)

for KEY_SERVICE_NUMBER in $(seq 1 $NUMBER_KEY_SERVICES)
do
    echo_if_not_silent "-- $KEY_SERVICE_NUMBER: Starting Key Service"

	if ! KEY_SERVICE=$(create_key_service $KEY_STORE); then
		echo_to_stderr_if_not_silent "-- $KEY_SERVICE_NUMBER: Key Service failed to start"
		exit 1
	fi

	echo_if_not_silent "-- $KEY_SERVICE_NUMBER: Key Service listening on $KEY_SERVICE"
done

#
# Key Service LB
#
echo_if_not_silent "Starting Key Service LB"
if ! KEY_SERVICE_LB=$(create_key_service_lb); then
    echo_to_stderr_if_not_silent "-- Key Service LB failed to start"
    exit 1
fi
echo_if_not_silent "-- Key Service LB listening on $KEY_SERVICE_LB"

#
# Auth Service(s)
#
echo_if_not_silent "Starting Auth Service(s)"

NUMBER_AUTH_SERVICES_PATTERN='\["auth_service"\,"number_of_servers"\]'
NUMBER_AUTH_SERVICES=$(get_from_json "$NUMBER_AUTH_SERVICES_PATTERN" "1" < $DEPLOYMENT_PROFILE)

for AUTH_SERVICE_NUMBER in $(seq 1 $NUMBER_AUTH_SERVICES)
do
    echo_if_not_silent "-- $AUTH_SERVICE_NUMBER: Starting Auth Service"

	if ! AUTH_SERVICE=$(create_auth_service $DATA_DIRECTORY $KEY_SERVICE_LB $APP_SERVICE_LB $NONCE_STORES); then
		echo_to_stderr_if_not_silent "-- Auth Service failed to start"
		exit 1
	fi

	echo_if_not_silent "-- Auth Service listening on $AUTH_SERVICE"
done

#
# Auth Service LB
#
echo_if_not_silent "Starting Auth Service LB"
if ! AUTH_SERVICE_LB=$(create_auth_service_lb); then
    echo_to_stderr_if_not_silent "-- Auth Service LB failed to start"
    exit 1
fi
echo_if_not_silent "-- Auth Service LB listening on $AUTH_SERVICE_LB"

#
# services now running ... let's provision some creds
#
PRINCIPAL="dave@example.com"
create_basic_creds $KEY_SERVICE $PRINCIPAL
create_mac_creds $KEY_SERVICE $PRINCIPAL

#
# Summarize the key items in the deployment
#
echo_if_not_silent "Deployment Highlights"

echo_if_not_silent "-- entry point @ $AUTH_SERVICE_LB"

if [ -r ~/.yar.creds ]; then
    echo_if_not_silent "-- creds in ~/.yar.creds"
fi

if [ -r ~/.yar.deployment ]; then
    echo_if_not_silent "-- description in ~/.yar.deployment"
fi

if [ -r ~/.yar.creds.random.set ]; then
    echo_if_not_silent "-- random set of creds in ~/.yar.creds.random.set"
fi

exit 0
