#!/bin/bash

if [ $# != 1 ]; then
    echo "usage: `basename $0` <mac key identifier>"
    exit 1
fi

curl -s http://localhost:8070/v1.0/creds/$1 | \
	pp.sh | \
	grep \"mac_algorithm\" | \
	sed 's/    \"mac_algorithm\": "//' | \
	sed 's/",//'

exit 0
