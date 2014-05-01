#!/usr/bin/env bash

if [ $# != 3 ]; then
    echo "usage: `basename $0` <port> <ram> <output_filename>"
    exit 1
fi

PORT=$1
RAM=$2
OUTPUT_FILENAME=$3

OUTPUT_DIRECTORY=$(python -c "import os; print os.path.dirname(os.path.abspath('$OUTPUT_FILENAME'))")
mkdir -p $OUTPUT_DIRECTORY

memcached -vv -m $RAM -p $PORT -u daemon >& $OUTPUT_FILENAME

exit $?
