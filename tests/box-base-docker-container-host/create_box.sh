#!/usr/bin/env bash

# this script creates the base docker container host box
# and loads the box into the local repo. WARNING this script
# is destructive in that it will remove/replace an existing box
# if it exists and destroy a running box if it exists

if [ $# != 0 ]; then
    echo "usage: `basename $0`"
    exit 1
fi

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

vagrant destroy --force

# non-zero exit status on error
vagrant box remove base-docker-container-host

cd "$SCRIPT_DIR_NAME"
vagrant up

vagrant package --output base-docker-container-host.box

vagrant box add base-docker-container-host base-docker-container-host.box

rm base-docker-container-host.box

vagrant destroy -f

exit 0
