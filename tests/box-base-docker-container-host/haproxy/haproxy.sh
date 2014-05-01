#!/usr/bin/env bash

if [ $# != 2 ]; then
    echo "usage: `basename $0` <cfg filename> <pid filename>"
    exit 1
fi

CFG_FILENAME=$1
PID_FILENAME=$2

haproxy -f "$CFG_FILENAME" -p "$PID_FILENAME"

#
# This script is intended to be used to start haproxy
# in a Docker container. If haproxy is configured to
# run in the background (daemon entry in the config
# file) the above statement will immediately return
# but if that's run a Docker container then the container
# will exit too:-( And so the idea for this super simple
# script was born. Instead of running haproxy directly
# run this script which will never exit by virtue of the
# while loop below (& the overhead of this script and the
# while loop is low).
#
# Why do we want haproxy to run in the background?
# If we want to add/remove servers from the tier
# over which haproxy is operating we need to create
# a new config file and restart haproxy using haproxy's
# -sf command line option. Same kind of thinking as
# above on the haproxy restart & the container exiting.
# As an aside, haproxy's -p command line option only
# works when haproxy is running in the background.
#
while true
do
    sleep 10
done

exit 0
