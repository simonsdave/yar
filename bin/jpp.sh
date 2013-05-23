#!/bin/bash

if [ $# != 0 ]; then
    echo "usage: `basename $0`"
    exit 1
fi

python -mjson.tool

exit 0
