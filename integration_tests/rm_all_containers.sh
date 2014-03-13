#!/usr/bin/env bash

# This is a simple bash script which resets the yar integration
# test environment by killing off all running docker containers
# and then removing all docker containers.

if [ "$(sudo docker ps --no-trunc -q | wc -l)" != "0" ]; then
    sudo docker kill `sudo docker ps --no-trunc -q` >& /dev/null
fi

if [ "$(sudo docker ps --no-trunc -a -q | wc -l)" != "0" ]; then
    sudo docker rm `sudo docker ps --no-trunc -a -q` >& /dev/null
fi

exit 0
