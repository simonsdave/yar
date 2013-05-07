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
HOST=localhost
PORT=8000
HTTP_METHOD=POST
AUTH_HEADER_CMD="$SCRIPTDIR/genahv.py \
	$HTTP_METHOD \
	$HOST \
	$PORT \
	$URI \
	$MAC_KEY_IDENTIFIER \
	$MAC_KEY \
	$MAC_ALGORITHM \
	'$CONTENT_TYPE' < $TMP_STDIN"
AUTH_HEADER_VALUE=`eval $AUTH_HEADER_CMD`

curl \
	-s \
	-v \
	-X $HTTP_METHOD \
	-H "Content-Type: $CONTENT_TYPE" \
	-H "Authorization: $AUTH_HEADER_VALUE" \
	--data-binary @$TMP_STDIN \
   http://$HOST:$PORT"$URI"

exit 0
