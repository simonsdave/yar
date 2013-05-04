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
CONTENT_TYPE="application/json; charset=utf-8"
TMP_STDIN=`mktemp -t DAS`
cat /dev/stdin > $TMP_STDIN
AUTH_HEADER_CMD="$SCRIPTDIR/genahv.py \
	GET \
	localhost \
	8000 \
	$URI \
	$MAC_KEY_IDENTIFIER \
	$MAC_KEY \
	$MAC_ALGORITHM \
	'$CONTENT_TYPE' < $TMP_STDIN"
AUTH_HEADER=`eval $AUTH_HEADER_CMD`

curl \
	-s \
	-v \
	-X GET \
	-H "Authorization: $AUTH_HEADER_VALUE" \
	-d @$TMP_STDIN \
   http://localhost:8000"$URI"

exit 0
