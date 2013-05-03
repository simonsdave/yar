#!/bin/bash

if [ $# != 2 ]; then
    echo "usage: `basename $0` <mac key identifier> <uri>"
    exit 1
fi

SCRIPTDIR="$( cd "$( dirname "$0" )" && pwd )"

MAC_KEY_IDENTIFIER=$1
MAC_KEY=`gmk.sh $MAC_KEY_IDENTIFIER`
MAC_ALGORITHM=`gma.sh $MAC_KEY_IDENTIFIER`
TS=`$SCRIPTDIR/gents.py`
NONCE=`$SCRIPTDIR/gennonce.py`
EXT=""
MAC=`genmac.py localhost 8000 GET $2 $TS $NONCE $EXT $MAC_KEY $MAC_ALGORITHM`

curl \
   -s \
   -v \
   -X GET \
   -H "Authorization: MAC id=\"$MAC_KEY_IDENTIFIER\", ts=\"$TS\", nonce=\"$NONCE\", ext=\"$EXT\", mac=\"$MAC\"" \
   http://localhost:8000"$2"

exit 0
