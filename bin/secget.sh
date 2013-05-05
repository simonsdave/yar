#!/bin/bash -xv

if [ $# != 2 ]; then
    echo "usage: `basename $0` <mac key identifier> <uri>"
    exit 1
fi

SCRIPTDIR="$( cd "$( dirname "$0" )" && pwd )"

URI=$2

MAC_KEY_IDENTIFIER=$1
MAC_KEY=`$SCRIPTDIR/gmk.sh $MAC_KEY_IDENTIFIER`
MAC_ALGORITHM=`$SCRIPTDIR/gma.sh $MAC_KEY_IDENTIFIER`
AUTH_HEADER=`$SCRIPTDIR/genahv.py \
	GET \
	localhost \
	8000 \
	$URI \
	$MAC_KEY_IDENTIFIER \
	$MAC_KEY $MAC_ALGORITHM`

curl \
   -s \
   -v \
   -X GET \
   -H "Authorization: $AUTH_HEADER" \
   http://localhost:8000"$URI"

exit 0
