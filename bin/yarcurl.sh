#!/bin/bash
#-------------------------------------------------------------------------------
#
# A wrapper around cURL that adds an HMAC HTTP Authorization header
# to a request directed at yar's auth server.
#
#-------------------------------------------------------------------------------

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

get_creds() {
    grep "^\\s*$1\\s*=" $YAR_CREDS | sed -e "s/^\\s*$1\\s*=\s*//"
}

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

URL=$(echo $2 | sed -e "s/^\\s*//")

SCHEME=$(echo $URL | sed -e "s/:.*//")

HOST=$(echo $URL | sed -e "s/^$SCHEME\:\/\///")
HOST=$(echo $HOST | sed -e "s/:.*$//")

PORT=$(echo $URL | sed -e "s/^$SCHEME\:\/\/$HOST\://")
PORT=$(echo $PORT | sed -e "s/\/.*//")

URI=$(echo $URL | sed -e "s/^$SCHEME\:\/\/$HOST\:$PORT//")

TIMESTAMP=$(date +%s)
NONCE=$(openssl rand -hex 16)

get_ext() {
	CONTENT_TYPE=${1:-}
	BODY=${2:-}
	if [ "$CONTENT_TYPE" == "" ] || [ "$BODY" == "" ]; then
		echo ""
	else
		echo -n $CONTENT_TYPE$BODY | openssl sha1 -hex
	fi
}
EXT=$(get_ext $CONTENT_TYPE $COPY_OF_STDIN0)

NRS=`mktemp -t DAS`
printf \
	'%s\n%s\n%s\n%s\n%s\n%s\n%s\n' \
	$TIMESTAMP \
	$NONCE \
	$HTTP_METHOD \
	$URI \
	$HOST \
	$PORT \
	$EXT >& $NRS
MAC=$(openssl dgst -sha1 -hmac "$MAC_KEY" < $NRS)
rm -f $NRS >& /dev/null

printf \
	-v AUTH_HEADER_VALUE \
	'MAC id="%s", ts="%s", nonce="%s", ext="%s", mac="%s"' \
	"$MAC_KEY_IDENTIFIER" \
	"$TIMESTAMP" \
	"$NONCE" \
	"$EXT" \
	"$MAC"

if [ "" != "$CONTENT_TYPE" ]; then
	curl \
		-s \
		$CURL_VERBOSE \
		-X $HTTP_METHOD \
		-H "Authorization: $AUTH_HEADER_VALUE" \
		-H "Content-Type: $CONTENT_TYPE" \
		--data-binary @$COPY_OF_STDIN \
	   $URL
else
	curl \
		-s \
		$CURL_VERBOSE \
		-X $HTTP_METHOD \
		-H "Authorization: $AUTH_HEADER_VALUE" \
	   $URL
fi

exit 0

#------------------------------------------------------------------- End-of-File
