#!/bin/bash

if [ $# != 1 ]; then
    echo "usage: `basename $0` <config_option_name>"
    exit 1
fi

SCRIPTDIR="$( cd "$( dirname "$0" )" && pwd )"
CONFIG_OPTION_NAME=$1
grep $1 "$SCRIPTDIR"/config.ini | sed -e "s/^\s*"$1"\=\s*//"

exit 0
