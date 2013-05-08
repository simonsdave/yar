#!/bin/bash -xv

usage_and_exit() {
	echo "usage: `basename $0` [GET|POST|PUT|DELETE] <mac key identifier> <uri>"
	exit 1
}

if [ $# != 3 ]; then
	usage_and_exit
fi

SCRIPTDIR="$( cd "$( dirname "$0" )" && pwd )"

HTTP_METHOD=`echo $1 | awk '{print toupper($0)}'`
MAC_KEY_IDENTIFIER=$2
URI=$3

case "$HTTP_METHOD" in
        GET)
            ;;
        POST)
            ;;
        DELETE)
            ;;
        PUT)
            ;;
        *)
            usage_and_exit
esac

MAC_KEY=`$SCRIPTDIR/gmk.sh $MAC_KEY_IDENTIFIER`
MAC_ALGORITHM=`$SCRIPTDIR/gma.sh $MAC_KEY_IDENTIFIER`
HOST=localhost
PORT=8000

if [ "POST" == "$HTTP_METHOD" ]; then
	CONTENT_TYPE="application/json; charset=utf-8"
	COPY_OF_STDIN=`mktemp -t DAS`
	cat /dev/stdin > $COPY_OF_STDIN
else
	CONTENT_TYPE=""
	COPY_OF_STDIN=/dev/null
fi

GEN_AUTH_HEADER_VALUE_CMD="$SCRIPTDIR/genahv.py \
    $HTTP_METHOD \
    $HOST \
    $PORT \
    $URI \
    $MAC_KEY_IDENTIFIER \
    $MAC_KEY \
    $MAC_ALGORITHM"
if [ "POST" == "$HTTP_METHOD" ]; then
    GEN_AUTH_HEADER_VALUE_CMD="$GEN_AUTH_HEADER_VALUE_CMD '$CONTENT_TYPE' < $COPY_OF_STDIN"
fi
AUTH_HEADER_VALUE=`eval $GEN_AUTH_HEADER_VALUE_CMD`

curl \
	-s \
	-v \
	-X $HTTP_METHOD \
	-H "Authorization: $AUTH_HEADER_VALUE" \
	-H "Content-Type: $CONTENT_TYPE" \
	--data-binary @$COPY_OF_STDIN \
   http://$HOST:$PORT"$URI"

exit 0