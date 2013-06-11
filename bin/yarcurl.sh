#!/bin/bash
#-------------------------------------------------------------------------------
#
# A wrapper around cURL that adds an HMAC HTTP Authorization header
# to a request directed at yar's auth server.
#
#-------------------------------------------------------------------------------

get_creds() {
    grep "^\\s*$1\\s*=" $YAR_CREDS | sed -e "s/^\\s*$1\\s*=\s*//"
}

usage() {
	echo "usage: `basename $0` [-v] [GET|POST|PUT|DELETE] <uri>"
}

CURL_VERBOSE=""
if [ 2 -lt $# ]; then
	if [ "-v" == $1 ]; then
		CURL_VERBOSE=-v
		shift
	fi
fi

if [ $# != 2 ]; then
	usage
	exit 1
fi

if [ "$YAR_CREDS" == "" ]; then
	YAR_CREDS=~/.yar.creds
fi

if [ ! -f $YAR_CREDS ]; then
	echo "`basename $0`: can't read from creds file '$YAR_CREDS'"
	exit 1
fi

SCRIPTDIR="$( cd "$( dirname "$0" )" && pwd )"

HTTP_METHOD=`echo $1 | awk '{print toupper($0)}'`
case "$HTTP_METHOD" in
        GET|DELETE)
			CONTENT_TYPE=""
			COPY_OF_STDIN=/dev/null
            ;;
        PUT|POST)
			CONTENT_TYPE="application/json; charset=utf-8"
			COPY_OF_STDIN=`mktemp -t DAS`
			cat /dev/stdin > $COPY_OF_STDIN
            ;;
        *)
            usage
			exit 1
esac

MAC_KEY_IDENTIFIER=`get_creds MAC_KEY_IDENTIFIER`
if [ "$MAC_KEY_IDENTIFIER" == "" ]; then
	echo "`basename $0` could not find mac key identifier"
	exit 1
fi

MAC_KEY=`get_creds MAC_KEY`
if [ "$MAC_KEY" == "" ]; then
	echo "`basename $0` could not find mac key"
	exit 1
fi

MAC_ALGORITHM=`get_creds MAC_ALGORITHM`
if [ "$MAC_ALGORITHM" == "" ]; then
	echo "`basename $0` could not find mac algorithm"
	exit 1
fi

URI=$2

HOST=localhost
PORT=8000

GEN_AUTH_HEADER_VALUE_CMD="$SCRIPTDIR/genahv.py \
    $HTTP_METHOD \
    $HOST \
    $PORT \
    $URI \
    $MAC_KEY_IDENTIFIER \
    $MAC_KEY \
    $MAC_ALGORITHM"
if [ "" != "$CONTENT_TYPE" ]; then
    GEN_AUTH_HEADER_VALUE_CMD="$GEN_AUTH_HEADER_VALUE_CMD '$CONTENT_TYPE' < $COPY_OF_STDIN"
fi
GEN_AUTH_HEADER_VALUE_CMD="$GEN_AUTH_HEADER_VALUE_CMD 2> /dev/null"
AUTH_HEADER_VALUE=`eval $GEN_AUTH_HEADER_VALUE_CMD` 
if [ "$AUTH_HEADER_VALUE" == "" ]; then
	echo "`basename $0` could not generate auth header value - check $YAR_CREDS"
	exit 1
fi

if [ "" != "$CONTENT_TYPE" ]; then
	curl \
		-s \
		$CURL_VERBOSE \
		-X $HTTP_METHOD \
		-H "Authorization: $AUTH_HEADER_VALUE" \
		-H "Content-Type: $CONTENT_TYPE" \
		--data-binary @$COPY_OF_STDIN \
	   http://$HOST:$PORT"$URI"
else
	curl \
		-s \
		$CURL_VERBOSE \
		-X $HTTP_METHOD \
		-H "Authorization: $AUTH_HEADER_VALUE" \
	   http://$HOST:$PORT"$URI"
fi

exit 0

#------------------------------------------------------------------- End-of-File
