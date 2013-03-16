#!/bin/bash

if [ $# != 0 ]; then
    echo "usage: `basename $0`"
    exit 1
fi

SCRIPTDIR="$( cd "$( dirname "$0" )" && pwd )"
DB_SERVER_IP=`"$SCRIPTDIR/get_config_option_value.sh" DB_SERVER_IP`
DB_SERVER_PORT=`"$SCRIPTDIR/get_config_option_value.sh" DB_SERVER_PORT`

curl -s -X GET http://$DB_SERVER_IP:$DB_SERVER_PORT | "$SCRIPTDIR/pp.sh"

exit 0
