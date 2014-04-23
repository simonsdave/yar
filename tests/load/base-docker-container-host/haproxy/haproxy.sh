#!/usr/bin/env bash

if [ $# != 2 ]; then
    echo "usage: `basename $0` <cfg filename> <pid filename>"
    exit 1
fi

CFG_FILENAME=$1
PID_FILENAME=$2

haproxy -f "$CFG_FILENAME" -p "$PID_FILENAME"

while true
do
    sleep 10
done

exit 0
