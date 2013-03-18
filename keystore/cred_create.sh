#!/bin/bash

if [ $# != 1 ]; then
    echo "usage: `basename $0` <mac-key-id>"
    exit 1
fi

SCRIPTDIR="$( cd "$( dirname "$0" )" && pwd )"

MAC_KEY_ID=$1
CRED_DATA_FILE_NAME=$SCRIPTDIR/cred_data/$MAC_KEY_ID.json
if [ ! -f "$CRED_DATA_FILE_NAME" ]; then
    echo "credentials data file not found: '$CRED_DATA_FILE_NAME'"
	exit 1
fi

DB_SERVER_IP=`"$SCRIPTDIR/get_config_option_value.sh" DB_SERVER_IP`
DB_SERVER_PORT=`"$SCRIPTDIR/get_config_option_value.sh" DB_SERVER_PORT`
DB_NAME=`"$SCRIPTDIR/get_config_option_value.sh" DB_NAME`

curl -s -X POST -H "Content-Type: application/json; charset=utf8" -d @"$CRED_DATA_FILE_NAME" http://$DB_SERVER_IP:$DB_SERVER_PORT/$DB_NAME | "$SCRIPTDIR/pp.sh"

exit 0
