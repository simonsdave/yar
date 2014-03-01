#!/usr/bin/env bash

# This is a simple bash script which resets the yar integration
# test environment by killing off all running docker containers
# and then removing all docker containers.

if [ "$(sudo docker ps -notrunc -a -q | wc -l)" != "0" ]; then
    sudo docker kill `sudo docker ps -notrunc -a -q` >& /dev/null
fi

if [ "$(sudo docker ps -notrunc -a -q | wc -l)" != "0" ]; then
    sudo docker rm `sudo docker ps -notrunc -a -q` >& /dev/null
fi

exit 0
