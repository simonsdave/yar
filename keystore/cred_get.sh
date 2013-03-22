#!/bin/bash

if [ $# != 1 ]; then
    echo "usage: `basename $0` \<mac key identifier\>"
    exit 1
fi

MAC_KEY_IDENTIFIER=$1

SCRIPTDIR="$( cd "$( dirname "$0" )" && pwd )"
DB_SERVER_IP=`"$SCRIPTDIR/get_config_option_value.sh" DB_SERVER_IP`
DB_SERVER_PORT=`"$SCRIPTDIR/get_config_option_value.sh" DB_SERVER_PORT`
DB_NAME=`"$SCRIPTDIR/get_config_option_value.sh" DB_NAME`

curl -s -X GET http://$DB_SERVER_IP:$DB_SERVER_PORT/$DB_NAME/$MAC_KEY_IDENTIFIER | "$SCRIPTDIR/pp.sh"

exit 0
