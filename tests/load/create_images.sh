#!/usr/bin/env bash

SCRIPT_DIR_NAME="$( cd "$( dirname "$0" )" && pwd )"

sudo docker build -t haproxy_img $SCRIPT_DIR_NAME/haproxy
sudo docker build -t memcached_img $SCRIPT_DIR_NAME/memcached
sudo docker build -t couchdb_img $SCRIPT_DIR_NAME/couchdb
sudo docker build -t yar_img $SCRIPT_DIR_NAME/yar

exit 0
